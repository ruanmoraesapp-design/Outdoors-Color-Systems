import sqlite3
import os

# Caminho para o banco de dados no diretório temporário
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'colorsystems.db')

def test_db_connection():
    try:
        # Tentar conectar ao banco de dados SQLite (ele cria o arquivo se não existir)
        print(f"Tentando conectar ao banco de dados SQLite em: {DB_PATH}")
        
        # Garantir que o diretório .tmp existe
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        connection = sqlite3.connect(DB_PATH)
        
        # Criar um cursor e executar uma query simples
        cursor = connection.cursor()
        cursor.execute("SELECT sqlite_version();")
        db_version = cursor.fetchone()
        
        print(f"[SUCESSO] Conexão bem sucedida!")
        print(f"Versão do SQLite: {db_version[0]}")
        
        # Fechar conexão
        cursor.close()
        connection.close()
        print("Conexão encerrada.")
        
    except Exception as error:
        print(f"[ERRO] Erro ao conectar ao banco de dados: {error}")
        return False
        
    return True

if __name__ == "__main__":
    test_db_connection()
