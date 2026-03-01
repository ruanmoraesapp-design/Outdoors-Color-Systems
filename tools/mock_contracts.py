import os
import sys
from datetime import datetime

sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys_path not in sys.path:
    sys.path.append(sys_path)
    
from tools.user_manager import create_user
from tools.contract_manager import create_contract
from tools.outdoor_manager import list_outdoors, update_outdoor_status

def setup_mock_contracts():
    print("=== Configurando Dados do Cliente para o Dashboard ===")
    
    # Busca outdoors disponíveis
    disp = list_outdoors(status_filter='disponivel')
    if not disp:
        print("Nenhum outdoor disponível no banco para atrelar a contrato.")
        return
        
    outdoor = disp[0] # Pega o primeiro para locar
    
    # Criar Usuário Extra
    print("\n[!] Registrando novo Cliente Contratante...")
    
    # Evitar falha de constraint caso a gente já tenha um log
    try:
        cliente_id = create_user(
            nome_razao_social="Pizzaria Forno a Lenha LTDA",
            cpf_cnpj="65.341.222/0001-90",
            email="pizzaria@colorsystems.com",
            senha_plana="65.341.222/0001-90", # Requisito 1.6 (CPF/CNPJ como senha)
            papel="cliente"
        )
    except Exception as e:
        print("Usuário já existe. Ignorando a criação.")
        cliente_id = None
        
    if not cliente_id:
        print("[AVISO] Como o cliente falhou por duplicidade vamos atar tudo àquele 'cliente@teste.com' da fase 2. Você pode logar normal com cliente@teste.com.")
        # Precisaremos de um ID. 
        import sqlite3
        conn = sqlite3.connect('.tmp/colorsystems.db')
        c = conn.cursor()
        c.execute("SELECT id FROM clientes WHERE email = 'cliente@teste.com'")
        cliente_id = c.fetchone()[0]
        conn.close()
    
    print(f"\n[!] Vinculando Contrato entre Cliente({cliente_id}) e Outdoor({outdoor['id']})")
    
    # Criamos o Contrato com boleto
    cid = create_contract(
        cliente_id=cliente_id,
        outdoor_id=outdoor['id'],
        data_inicio="2026-03-01",
        data_teorica_fim="2026-09-01",
        valor_mensal_acordado=1000.00
    )
    
    print("\n[!] Atualizando status do outdoor para 'ocupado'...")
    update_outdoor_status(outdoor['id'], 'ocupado')
    
    print("\n--- TESTE FINALIZADO ---")

if __name__ == "__main__":
    setup_mock_contracts()
