import sqlite3
import os
import sys
import uuid
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'colorsystems.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password, salt=None):
    """
    Gera um hash SHA-256 da senha.
    Se o salt não for fornecido, cria um novo (para cadastros).
    Retorna a string formatada 'salt$hash'
    """
    if not salt:
        salt = os.urandom(16).hex()
    
    # Hash usando PBKDF2
    key = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    )
    return f"{salt}${key.hex()}"

def verify_password(stored_password, provided_password):
    """
    Verifica se a senha fornecida corresponde ao hash armazenado.
    """
    if '$' not in stored_password:
        return False
        
    salt, _ = stored_password.split('$')
    return stored_password == hash_password(provided_password, salt)

def create_user(nome_razao_social, cpf_cnpj, email, senha_plana, papel='cliente', telefone=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Validação do papel
        if papel not in ['cliente', 'admin']:
            raise ValueError("Papel inválido. Deve ser 'cliente' ou 'admin'.")
            
        user_id = str(uuid.uuid4())
        senha_hash = hash_password(senha_plana)
        
        cursor.execute('''
            INSERT INTO clientes (
                id, nome_razao_social, cpf_cnpj, email, telefone, senha_hash, papel
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, nome_razao_social, cpf_cnpj, email, telefone, senha_hash, papel))
        
        conn.commit()
        print(f"[SUCESSO] Usuário '{email}' criado com papel de {papel}.")
        return user_id
        
    except sqlite3.IntegrityError as e:
        print(f"[ERRO] Falha de integridade (Email ou CPF/CNPJ já existente): {e}")
        return None
    except Exception as e:
        print(f"[ERRO] Falha ao criar usuário: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def authenticate_user(email, senha_plana):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM clientes WHERE email = ?', (email,))
        user_row = cursor.fetchone()
        
        if not user_row:
            print("[ALERTA] Email não encontrado.")
            return False, None
            
        user = dict(user_row)
        
        # Validar senha
        if verify_password(user['senha_hash'], senha_plana):
            # Remover o hash do retorno por segurança
            del user['senha_hash']
            print(f"[SUCESSO] Login autorizado para: {user['nome_razao_social']}")
            return True, user
        else:
            print("[ALERTA] Senha incorreta.")
            return False, None
            
    except sqlite3.Error as e:
        print(f"[ERRO] Falha no banco de dados durante autenticação: {e}")
        return False, None
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python user_manager.py [test_auth]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "test_auth":
        print("\n--- INICIANDO TESTE DE AUTENTICAÇÃO ---")
        
        test_email = "admin@colorsystems.com"
        test_pass = "senha_super_segura123"
        
        print("\n1. Criando Admin...")
        uid = create_user(
            nome_razao_social="Administrador Sistema",
            cpf_cnpj="00000000000000",
            email=test_email,
            senha_plana=test_pass,
            papel="admin"
        )
        
        print("\n2. Testando Login com Senha Correta...")
        success, user_data = authenticate_user(test_email, test_pass)
        print(f"Resultado: {success} | Dados: {user_data['nome_razao_social'] if user_data else None}")
        
        print("\n3. Testando Login com Senha Incorreta...")
        success, _ = authenticate_user(test_email, "senha_errada")
        print(f"Resultado: {success}")
        
        print("\n4. Testando Duplicação de Email...")
        create_user("Clonador", "11111111111111", test_email, "123", "cliente")
        
        print("\n--- TESTE CONCLUÍDO ---")

def list_clients():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_razao_social, cpf_cnpj, email, telefone FROM clientes WHERE papel = 'cliente'")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"[ERRO] Falha ao listar clientes: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def get_client_by_id(client_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_razao_social, cpf_cnpj, email, telefone FROM clientes WHERE id = ?", (client_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except sqlite3.Error as e:
        print(f"[ERRO] Falha ao buscar cliente: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()
