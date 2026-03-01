import sqlite3
import os
import sys
import uuid
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'colorsystems.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    # Retorna as linhas como dicionários em vez de tuplas
    conn.row_factory = sqlite3.Row
    return conn

def create_outdoor(nome, localizacao, preco, status='disponivel', lat=None, lng=None, dimensoes=None, especificacoes=None, fotos=r'[]', bairro=None, link_google_maps=None, foto_url=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        outdoor_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO outdoors (
                id, nome_identificador, localizacao_texto, preco_mensal_base, 
                status, lat, lng, dimensoes, especificacoes, fotos, bairro, link_google_maps, foto_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (outdoor_id, nome, localizacao, preco, status, lat, lng, dimensoes, especificacoes, fotos, bairro, link_google_maps, foto_url))
        
        conn.commit()
        print(f"[SUCESSO] Outdoor criado com ID: {outdoor_id}")
        return outdoor_id
    except sqlite3.Error as e:
        print(f"[ERRO] Falha ao criar outdoor: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def list_outdoors(status_filter=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if status_filter:
            cursor.execute('SELECT * FROM outdoors WHERE status = ?', (status_filter,))
        else:
            cursor.execute('SELECT * FROM outdoors')
            
        rows = cursor.fetchall()
        outdoors = [dict(row) for row in rows]
        return outdoors
    except sqlite3.Error as e:
        print(f"[ERRO] Falha ao listar outdoors: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def update_outdoor(outdoor_id, nome=None, localizacao=None, preco=None, status=None, lat=None, lng=None, dimensoes=None, especificacoes=None, fotos=None, bairro=None, link_google_maps=None, foto_url=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Validar status e construir query
        query_parts = []
        params = []
        
        if nome is not None:
            query_parts.append("nome_identificador = ?")
            params.append(nome)
        if localizacao is not None:
            query_parts.append("localizacao_texto = ?")
            params.append(localizacao)
        if preco is not None:
            query_parts.append("preco_mensal_base = ?")
            params.append(preco)
        if status is not None:
            if status not in ['disponivel', 'ocupado', 'manutencao']:
                raise ValueError("Status inválido.")
            query_parts.append("status = ?")
            params.append(status)
        if lat is not None:
            query_parts.append("lat = ?")
            params.append(lat)
        if lng is not None:
            query_parts.append("lng = ?")
            params.append(lng)
        if dimensoes is not None:
            query_parts.append("dimensoes = ?")
            params.append(dimensoes)
        if especificacoes is not None:
            query_parts.append("especificacoes = ?")
            params.append(especificacoes)
        if fotos is not None:
            query_parts.append("fotos = ?")
            params.append(fotos)
        if bairro is not None:
            query_parts.append("bairro = ?")
            params.append(bairro)
        if link_google_maps is not None:
            query_parts.append("link_google_maps = ?")
            params.append(link_google_maps)
        if foto_url is not None:
            query_parts.append("foto_url = ?")
            params.append(foto_url)
        if not query_parts:
            # Nada para atualizar
            return True

        agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query_parts.append("atualizado_em = ?")
        params.append(agora)
        
        params.append(outdoor_id)
        
        query = "UPDATE outdoors SET " + ", ".join(query_parts) + " WHERE id = ?"
        
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            print(f"[ERRO] Outdoor ID {outdoor_id} não encontrado.")
            return False
            
        conn.commit()
        print(f"[SUCESSO] Outdoor {outdoor_id} atualizado.")
        return True
    except (sqlite3.Error, ValueError) as e:
        print(f"[ERRO] Falha ao atualizar outdoor: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def delete_outdoor(outdoor_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM outdoors WHERE id = ?', (outdoor_id,))
        
        if cursor.rowcount == 0:
            print(f"[ERRO] Outdoor ID {outdoor_id} não encontrado para deleção.")
            return False
            
        conn.commit()
        print(f"[SUCESSO] Outdoor {outdoor_id} deletado permanentemente.")
        return True
    # O RESTRICT da Foreign Key lançará um IntegrityError se houver contratos atrelados
    except sqlite3.IntegrityError:
        print(f"[ERRO] Não é possível deletar outdoor que possui contratos registrados. Mude o status para 'manutencao'.")
        return False
    except sqlite3.Error as e:
        print(f"[ERRO] Falha ao deletar outdoor: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def get_outdoor_by_id(outdoor_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM outdoors WHERE id = ?', (outdoor_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except sqlite3.Error as e:
        print(f"[ERRO] Falha ao buscar outdoor: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python outdoor_manager.py [test_crud]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "test_crud":
        print("\n--- INICIANDO TESTE CRUD DE OUTDOORS ---")
        
        # 1. Create
        print("\n1. Criando outdoor de teste...")
        oid = create_outdoor(
            nome="Painel Centro Comercial", 
            localizacao="Av. Principal, 1000 - Centro", 
            preco=1200.00,
            dimensoes="9x3m"
        )
        
        # 2. Read
        print("\n2. Listando outdoors disponíveis...")
        disponiveis = list_outdoors(status_filter='disponivel')
        print(f"Encontrados: {len(disponiveis)}")
        for d in disponiveis:
            print(f" - {d['nome_identificador']} | {d['status']} | R$ {d['preco_mensal_base']}")
            
        # 3. Update
        if oid:
            print("\n3. Atualizando status do outdoor para 'manutencao'...")
            update_outdoor_status(oid, 'manutencao')
            
            # 4. Delete
            print("\n4. Deletando outdoor de teste...")
            delete_outdoor(oid)
            
        print("\n--- TESTE CONCLUÍDO ---")
