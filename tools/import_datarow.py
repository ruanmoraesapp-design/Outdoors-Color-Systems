import uuid
import json
import os
import sys
from datetime import datetime, timedelta

# Garantindo acesso aos modulos da raiz
sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys_path not in sys.path:
    sys.path.append(sys_path)

from tools.outdoor_manager import create_outdoor
from tools.user_manager import create_user, get_connection
from tools.contract_manager import create_contract

def normalize_string(s):
    return "".join(c for c in s if c.isalnum()).lower()

def run_import():
    json_path = os.path.join(sys_path, '.tmp', 'mock_datarow.json')
    
    if not os.path.exists(json_path):
        print(f"[ERRO] Arquivo JSON nao encontrado em: {json_path}")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    conn = get_connection()
    cursor = conn.cursor()
    
    print(f"[IMPORTADOR] Iniciando importacao de {len(data)} registros do Datarow...")
    
    outdoors_criados = 0
    clientes_criados = 0
    contratos_criados = 0
    
    # Resetando as tabelas para a nova rodada limpa de testes de importacao
    cursor.execute('DELETE FROM boletos;')
    cursor.execute('DELETE FROM contratos;')
    cursor.execute('DELETE FROM outdoors;')
    cursor.execute('DELETE FROM clientes WHERE papel = "cliente";')
    conn.commit()

    hoje = datetime.now()
    daqui_um_ano = hoje + timedelta(days=365)
    data_inicio_str = hoje.strftime('%Y-%m-%d')
    data_fim_str = daqui_um_ano.strftime('%Y-%m-%d')
    
    for item in data:
        # Extrai os dados do JSON
        nome = item.get('id')
        endereco = item.get('endereco')
        material = item.get('material')
        dimensoes = item.get('dimensoes')
        status_txt = item.get('status', '').lower()
        cliente_nome = item.get('cliente')
        
        # Converte status para o padrao do nosso banco
        status_bd = 'ocupado' if 'ocupado' in status_txt else 'disponivel'
        # Se veio vazio mas tem cliente, forca ocupado
        if cliente_nome and status_bd == 'disponivel':
            status_bd = 'ocupado'
            
        print(f"[PROCESSANDO] {nome} - {status_bd}...")
        
        # Cria Outdoor
        outdoor_id = create_outdoor(
            nome=nome,
            localizacao=endereco,
            preco=800.00,  # Preco padrao de importacao
            status=status_bd,
            dimensoes=dimensoes,
            especificacoes=f"Material: {material}"
        )
        outdoors_criados += 1
        
        # Se tem cliente associado, gerencia o cliente e vincula
        if cliente_nome and outdoor_id:
            # Verifica se o cliente ja existe com esse nome_razao_social
            cursor.execute('SELECT id FROM clientes WHERE nome_razao_social = ?', (cliente_nome,))
            row = cursor.fetchone()
            
            if row:
                cliente_id = row['id']
                print(f"  > Cliente existente encontrado: {cliente_nome}")
            else:
                # Criar novo cliente
                email_fake = f"{normalize_string(cliente_nome)}@importacao.com"
                senha_padrao = "color123"
                
                cursor.execute("SELECT email FROM clientes WHERE email = ?", (email_fake,))
                if cursor.fetchone():
                    # Para evitar colisao caso normalizacao falhe e atinja 2 nomes iguais mas strings originais diferentes
                    email_fake = f"{normalize_string(cliente_nome)}_{outdoors_criados}@importacao.com"
                
                try:
                    create_user(
                        nome_razao_social=cliente_nome,
                        cpf_cnpj=f"000.{str(uuid.uuid4())[:3]}.000-00", # cpf unico mockado
                        email=email_fake,
                        senha_plana=senha_padrao,
                        papel='cliente',
                        telefone="(89) 00000-0000"
                    )
                    clientes_criados += 1
                    
                    # Pegar o ID recem criado
                    cursor.execute('SELECT id FROM clientes WHERE nome_razao_social = ?', (cliente_nome,))
                    cliente_id = cursor.fetchone()['id']
                    print(f"  > NOVO Cliente criado: {cliente_nome} (Login: {email_fake})")
                except Exception as e:
                    print(f"  > [ERRO] Falha ao criar cliente {cliente_nome}: {e}")
                    cliente_id = None
            
            # Vincula via Contrato
            if cliente_id:
                try:
                    create_contract(
                        cliente_id=cliente_id,
                        outdoor_id=outdoor_id,
                        data_inicio=data_inicio_str,
                        data_teorica_fim=data_fim_str,
                        valor_mensal_acordado=800.00
                    )
                    contratos_criados += 1
                    print(f"  > Contrato Ativo gerado e Billetes programados.")
                except Exception as e:
                    print(f"  > [ERRO] Falha ao criar contrato para o outdoor {nome}: {e}")

    conn.close()
    print("\n" + "="*50)
    print("IMPORTACAO FINALIZADA COM SUCESSO!")
    print(f"Outdoors Importados: {outdoors_criados}")
    print(f"Novos Clientes Cadastrados: {clientes_criados}")
    print(f"Contratos Abertos: {contratos_criados}")
    print("="*50 + "\n")

if __name__ == '__main__':
    run_import()
