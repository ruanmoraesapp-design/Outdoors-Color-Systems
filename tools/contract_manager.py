import os
import sys
import uuid
import sqlite3
from datetime import datetime, timedelta

sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys_path not in sys.path:
    sys.path.append(sys_path)
    
from tools.user_manager import get_connection

def _add_months(source_date, months):
    """Adiciona N meses a uma data de forma segura sem dependência externa."""
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    import calendar
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return source_date.replace(year=year, month=month, day=day)

def create_contract(cliente_id, outdoor_id, data_inicio, data_teorica_fim, valor_mensal_acordado, status="ativo"):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        contrato_id = str(uuid.uuid4())
        valor_mensal = float(valor_mensal_acordado)
        
        cursor.execute('''
            INSERT INTO contratos (id, cliente_id, outdoor_id, data_inicio, data_teorica_fim, status, valor_mensal_acordado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (contrato_id, cliente_id, outdoor_id, data_inicio, data_teorica_fim, status, valor_mensal))
        
        # Calcular número de meses entre início e fim
        dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        dt_fim = datetime.strptime(data_teorica_fim, '%Y-%m-%d')
        
        meses = []
        current = dt_inicio
        while current < dt_fim:
            meses.append(current)
            current = _add_months(current, 1)
        
        # Se não gerou nenhum mês (mesmo mês), garantir pelo menos 1
        if not meses:
            meses.append(dt_inicio)
        
        num_meses = len(meses)
        
        # Gerar boleto individual para cada mês
        for i, mes_dt in enumerate(meses):
            boleto_id = str(uuid.uuid4())
            mes_ref = mes_dt.strftime('%m/%Y')
            vencimento = mes_dt.replace(day=10).strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO boletos (id, contrato_id, mes_referencia, valor, data_vencimento, status_pagamento)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (boleto_id, contrato_id, mes_ref, valor_mensal, vencimento, 'pendente'))
        
        # Gerar boleto geral (total do período) se houver mais de 1 mês
        if num_meses > 1:
            boleto_geral_id = str(uuid.uuid4())
            valor_total = valor_mensal * num_meses
            ref_geral = f"TOTAL ({meses[0].strftime('%m/%Y')} a {meses[-1].strftime('%m/%Y')})"
            venc_geral = dt_inicio.replace(day=10).strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO boletos (id, contrato_id, mes_referencia, valor, data_vencimento, status_pagamento)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (boleto_geral_id, contrato_id, ref_geral, valor_total, venc_geral, 'pendente'))

        conn.commit()
        print(f"[SUCESSO] Contrato {contrato_id} gerado com {num_meses} boleto(s) mensais.")
        return contrato_id
        
    except sqlite3.Error as e:
        print(f"[ERRO] Falha ao criar contrato: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def get_contracts_by_client(cliente_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = '''
            SELECT c.*, o.nome_identificador as outdoor_nome, o.localizacao_texto as outdoor_loc, o.foto_url as outdoor_foto 
            FROM contratos c
            JOIN outdoors o ON c.outdoor_id = o.id
            WHERE c.cliente_id = ?
        '''
        cursor.execute(query, (cliente_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"[ERRO] Falha as buscar contratos: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def get_active_contract_by_outdoor(outdoor_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = '''
            SELECT c.*, cl.nome_razao_social as cliente_nome
            FROM contratos c
            JOIN clientes cl ON c.cliente_id = cl.id
            WHERE c.outdoor_id = ? AND c.status = 'ativo'
        '''
        cursor.execute(query, (outdoor_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except sqlite3.Error as e:
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def get_boletos_by_contract(contrato_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM boletos WHERE contrato_id = ?', (contrato_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def update_boleto_status(boleto_id, novo_status):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE boletos SET status_pagamento = ? WHERE id = ?", (novo_status, boleto_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"[ERRO] {e}")
    finally:
        if 'conn' in locals():
            conn.close()
