import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename

# Importando nossos modulos da arquitetura (Fase 3)
sys_path = os.path.dirname(os.path.abspath(__file__))
if sys_path not in __import__("sys").path:
    __import__("sys").path.append(sys_path)

from tools.outdoor_manager import list_outdoors, get_outdoor_by_id, create_outdoor, update_outdoor
from tools.user_manager import authenticate_user, list_clients, create_user, get_client_by_id
from tools.contract_manager import get_contracts_by_client, get_active_contract_by_outdoor, get_boletos_by_contract, create_contract, update_boleto_status

from datetime import timedelta
app = Flask(__name__)
# Chave secreta super simples para fins de ambiente local e sessoes
app.secret_key = 'super_secret_color_systems_key'
app.permanent_session_lifetime = timedelta(days=30)
UPLOAD_FOLDER = os.path.join(sys_path, 'static', 'images', 'outdoors')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(sys_path, '.tmp'), exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Filtro Jinja2 para parsear JSON de fotos
@app.template_filter('parse_fotos')
def parse_fotos_filter(value):
    """Converte foto_url (string JSON ou URL simples) em lista de URLs."""
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return parsed
        return [str(parsed)]
    except (json.JSONDecodeError, TypeError):
        return [value] if value else []

@app.route('/')
def home():
    # Carregar todos os outdoors para permitir o filtro JS no frontend
    outdoors = list_outdoors()
    # Listar bairros unicos
    bairros = sorted(list(set(o['bairro'] for o in outdoors if o.get('bairro'))))
    return render_template('index.html', outdoors=outdoors, bairros=bairros)

@app.route('/outdoor/<id>')
def outdoor_detail(id):
    outdoor = get_outdoor_by_id(id)
    if not outdoor:
        return "Outdoor não encontrado", 404
        
    return render_template('outdoor_detail.html', outdoor=outdoor)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        success, user = authenticate_user(email, senha)
        if success:
            session.permanent = True
            session['user_id'] = user['id']
            session['papel'] = user['papel']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="E-mail ou senha incorretos")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    role = session.get('papel')
    user_id = session.get('user_id')
    
    from datetime import datetime
    hoje = datetime.now().date()
    alertas_vencimento = 0

    if role == 'admin':
        # Carregar todos os outdoors
        all_outdoors = list_outdoors()
        
        # Buscar cliente vinculado se estiver ocupado
        for outdoor in all_outdoors:
            # Converte row_factory de sqlite3 para dict para podermos injetar dados facilmente
            import collections
            if isinstance(outdoor, sqlite3.Row) if 'sqlite3' in globals() else type(outdoor).__name__ == 'Row':
                outdoor = dict(outdoor) # Will not re-assign since list_outdoors returns dicts or sqlite3 rows
                
            if outdoor['status'] == 'ocupado':
                contract = get_active_contract_by_outdoor(outdoor['id'])
                if contract:
                    outdoor['cliente_nome'] = contract['cliente_nome']
                    outdoor['data_inicio'] = contract['data_inicio']
                    outdoor['data_teorica_fim'] = contract['data_teorica_fim']
                    
                    dt_inicio = datetime.strptime(contract['data_inicio'], '%Y-%m-%d').date()
                    dt_fim = datetime.strptime(contract['data_teorica_fim'], '%Y-%m-%d').date()
                    
                    dias_restantes = (dt_fim - hoje).days
                    outdoor['dias_restantes'] = dias_restantes
                    
                    if dias_restantes <= 30:
                        outdoor['prazo_status'] = 'vencendo'
                        alertas_vencimento += 1
                    elif (hoje - dt_inicio).days <= 30:
                        outdoor['prazo_status'] = 'recente'
                    else:
                        outdoor['prazo_status'] = 'normal'
                    
        return render_template('dashboard_admin.html', outdoors=all_outdoors, user_role=role, alertas_vencimento=alertas_vencimento)
    else:
        # Carregar contratos do cliente logado
        contracts = get_contracts_by_client(user_id)
        for contract in contracts:
            contract['boletos'] = get_boletos_by_contract(contract['id'])
            if contract['status'] == 'ativo':
                dt_fim = datetime.strptime(contract['data_teorica_fim'], '%Y-%m-%d').date()
                dias_restantes = (dt_fim - hoje).days
                contract['dias_restantes'] = dias_restantes
                
                if dias_restantes <= 30:
                    contract['prazo_status'] = 'vencendo'
                    alertas_vencimento += 1
            
        return render_template('dashboard_cliente.html', contracts=contracts, user_role=role, alertas_vencimento=alertas_vencimento)

@app.route('/admin/clientes')
def admin_clientes():
    if session.get('papel') != 'admin':
        return redirect(url_for('dashboard'))
    
    clientes = list_clients()
    return render_template('admin_clientes.html', clientes=clientes)

@app.route('/admin/cliente/new', methods=['GET', 'POST'])
def cliente_new():
    if session.get('papel') != 'admin':
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        nome = request.form.get('nome_razao_social')
        cpf = request.form.get('cpf_cnpj')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        
        # Cria o cliente com a senha provisória sendo o próprio documento
        create_user(nome, cpf, email, cpf, 'cliente', telefone=telefone)
        return redirect(url_for('admin_clientes'))
        
    return render_template('admin_cliente_form.html')

@app.route('/admin/cliente/<id>')
def cliente_detalhe(id):
    if session.get('papel') != 'admin':
        return redirect(url_for('dashboard'))
        
    cliente = get_client_by_id(id)
    if not cliente:
        return redirect(url_for('admin_clientes'))
        
    contracts = get_contracts_by_client(id)
    for contract in contracts:
        contract['boletos'] = get_boletos_by_contract(contract['id'])
        
    outdoors_livres = list_outdoors(status_filter='disponivel')
    
    return render_template('admin_cliente_detalhe.html', cliente=cliente, contracts=contracts, outdoors_livres=outdoors_livres)

@app.route('/admin/cliente/<id>/vincular', methods=['POST'])
def vincular_outdoor(id):
    if session.get('papel') != 'admin':
        return redirect(url_for('dashboard'))
        
    outdoor_id = request.form.get('outdoor_id')
    data_inicio = request.form.get('data_inicio')
    data_teorica_fim = request.form.get('data_teorica_fim')
    valor_mensal = request.form.get('valor_mensal')
    
    if outdoor_id and data_inicio and data_teorica_fim and valor_mensal:
        create_contract(id, outdoor_id, data_inicio, data_teorica_fim, valor_mensal)
        update_outdoor(outdoor_id, status='ocupado')
        
    return redirect(url_for('cliente_detalhe', id=id))

@app.route('/admin/boleto/<id>/pay', methods=['POST'])
def pay_boleto(id):
    if session.get('papel') != 'admin':
        return redirect(url_for('dashboard'))
        
    cliente_id = request.form.get('cliente_id')
    update_boleto_status(id, 'pago')
    
    return redirect(url_for('cliente_detalhe', id=cliente_id))

@app.route('/admin/outdoor/new', methods=['GET', 'POST'])
def outdoor_new():
    if session.get('papel') != 'admin':
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        nome = request.form.get('nome_identificador')
        preco = request.form.get('preco_mensal_base')
        status = request.form.get('status', 'disponivel')
        especificacoes = request.form.get('especificacoes')
        dimensoes = request.form.get('dimensoes')
        bairro = request.form.get('bairro')
        link_maps = request.form.get('link_google_maps')
        localizacao = request.form.get('localizacao_texto')
        
        foto_urls = []
        fotos = request.files.getlist('fotos')
        for foto in fotos:
            if foto and foto.filename:
                filename = secure_filename(f"{nome.replace(' ', '_')}_{foto.filename}")
                foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                foto_urls.append(f"/static/images/outdoors/{filename}")

        foto_url_json = json.dumps(foto_urls) if foto_urls else None

        create_outdoor(
            nome=nome, localizacao=localizacao, preco=preco, status=status,
            dimensoes=dimensoes, especificacoes=especificacoes, bairro=bairro,
            link_google_maps=link_maps, foto_url=foto_url_json
        )
        return redirect(url_for('dashboard'))
        
    # Buscar bairros unicos para o datalist
    all_o = list_outdoors()
    bairros = sorted(list(set(o['bairro'] for o in all_o if o.get('bairro'))))
    
    return render_template('outdoor_form.html', action='new', bairros=bairros)

@app.route('/admin/outdoor/<id>/edit', methods=['GET', 'POST'])
def outdoor_edit(id):
    if session.get('papel') != 'admin':
        return redirect(url_for('dashboard'))
        
    outdoor = get_outdoor_by_id(id)
    if not outdoor:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nome = request.form.get('nome_identificador')
        preco = request.form.get('preco_mensal_base')
        status = request.form.get('status')
        especificacoes = request.form.get('especificacoes')
        dimensoes = request.form.get('dimensoes')
        bairro = request.form.get('bairro')
        link_maps = request.form.get('link_google_maps')
        localizacao = request.form.get('localizacao_texto')
        
        # Carregar fotos existentes
        existing_fotos = []
        if outdoor.get('foto_url'):
            try:
                existing_fotos = json.loads(outdoor['foto_url'])
            except (json.JSONDecodeError, TypeError):
                if outdoor['foto_url']:
                    existing_fotos = [outdoor['foto_url']]
        
        # Adicionar novas fotos
        fotos = request.files.getlist('fotos')
        for foto in fotos:
            if foto and foto.filename:
                filename = secure_filename(f"{nome.replace(' ', '_')}_{foto.filename}")
                foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                existing_fotos.append(f"/static/images/outdoors/{filename}")

        foto_url_json = json.dumps(existing_fotos) if existing_fotos else outdoor.get('foto_url')

        update_outdoor(
            id, nome=nome, localizacao=localizacao, preco=preco, status=status,
            dimensoes=dimensoes, especificacoes=especificacoes, bairro=bairro,
            link_google_maps=link_maps, foto_url=foto_url_json
        )
        return redirect(url_for('dashboard'))
        
    all_o = list_outdoors()
    bairros = sorted(list(set(o['bairro'] for o in all_o if o.get('bairro'))))
    
    return render_template('outdoor_form.html', action='edit', outdoor=outdoor, bairros=bairros)

if __name__ == '__main__':
    # Cria a pasta .tmp no inicio para o banco de dados caso nao exista
    os.makedirs(os.path.join(sys_path, '.tmp'), exist_ok=True)
    app.run(debug=True, port=5000)
