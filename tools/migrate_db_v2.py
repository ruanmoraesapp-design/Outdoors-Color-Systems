import os
import sys
import sqlite3

sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys_path not in sys.path:
    sys.path.append(sys_path)

from tools.user_manager import get_connection

def migrate_outdoors():
    print("Iniciando migração da tabela outdoors...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Array de novas colunas e tipos
        new_columns = [
            ("bairro", "TEXT"),
            ("link_google_maps", "TEXT"),
            ("foto_url", "TEXT")
        ]
        
        for col_name, col_type in new_columns:
            try:
                # SQLite não suporta IF NOT EXISTS no ADD COLUMN de forma simples
                cursor.execute(f"ALTER TABLE outdoors ADD COLUMN {col_name} {col_type}")
                print(f"[OK] Coluna '{col_name}' adicionada com sucesso.")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"[SKIP] Coluna '{col_name}' já existe.")
                else:
                    print(f"[ERRO] Falha ao adicionar coluna '{col_name}': {e}")
                    
        conn.commit()
        print("Migração concluída.")
    except Exception as e:
        print(f"Erro na conexão com o banco: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    migrate_outdoors()
