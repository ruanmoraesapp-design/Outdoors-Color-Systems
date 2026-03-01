import sqlite3
import os
import sys

# Caminho para o banco de dados no diretório temporário
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'colorsystems.db')

def setup_database():
    try:
        print(f"[{'INFO'}] Preparando banco de dados SQLite em: {DB_PATH}")
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        # Conecta (ou cria) o banco
        conn = sqlite3.connect(DB_PATH)
        
        # Habilita suporte a chaves estrangeiras
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        # 1. Tabela Outdoors
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS outdoors (
            id TEXT PRIMARY KEY,
            nome_identificador TEXT NOT NULL,
            localizacao_texto TEXT NOT NULL,
            lat REAL,
            lng REAL,
            dimensoes TEXT,
            especificacoes TEXT,
            fotos TEXT,
            status TEXT NOT NULL CHECK(status IN ('disponivel', 'ocupado', 'manutencao')),
            preco_mensal_base REAL NOT NULL,
            bairro TEXT,
            link_google_maps TEXT,
            foto_url TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        ''')

        # 2. Tabela Clientes / Admins
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id TEXT PRIMARY KEY,
            nome_razao_social TEXT NOT NULL,
            cpf_cnpj TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telefone TEXT,
            senha_hash TEXT NOT NULL,
            papel TEXT NOT NULL CHECK(papel IN ('cliente', 'admin')),
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        ''')

        # 3. Tabela Contratos de Aluguel
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contratos (
            id TEXT PRIMARY KEY,
            cliente_id TEXT NOT NULL,
            outdoor_id TEXT NOT NULL,
            data_inicio DATE NOT NULL,
            data_teorica_fim DATE NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('ativo', 'encerrado', 'inadimplente', 'pendente_aprovacao')),
            valor_mensal_acordado REAL NOT NULL,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE RESTRICT,
            FOREIGN KEY (outdoor_id) REFERENCES outdoors (id) ON DELETE RESTRICT
        );
        ''')

        # 4. Tabela Boletos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS boletos (
            id TEXT PRIMARY KEY,
            contrato_id TEXT NOT NULL,
            mes_referencia TEXT NOT NULL, -- Formato MM/YYYY
            valor REAL NOT NULL,
            data_vencimento DATE NOT NULL,
            status_pagamento TEXT NOT NULL CHECK(status_pagamento IN ('pendente', 'pago', 'atrasado')),
            url_boleto_pdf TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contrato_id) REFERENCES contratos (id) ON DELETE RESTRICT
        );
        ''')

        conn.commit()
        print(f"[{'SUCESSO'}] Tabelas criadas com sucesso.")
        
    except sqlite3.Error as e:
        print(f"[{'ERRO'}] Falha ao configurar tabelas do banco de dados: {e}")
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_database()
