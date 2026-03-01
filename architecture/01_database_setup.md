# SOP 01: Setup do Banco de Dados (SQLite)

## Objetivo
Criar a base de dados relacional e aplicar o Esquema de Dados (Data Schema) definido na Constituição do Projeto (`gemini.md`) no ambiente transacional (SQLite local na pasta `.tmp/`).

## Camada de Navegação (Inputs Esperados)
- Execução direta do script via terminal na raiz do projeto.
- Variáveis de ambiente (opcionais para o nome do arquivo, mas pré-definidas no handshake).

## Lógica de Execução (Regras)
1. **Conexão:** Utilizar a biblioteca nativa `sqlite3`. Apontar para `DB_PATH = .tmp/colorsystems.db`.
2. **Idempotência:** As tabelas devem ser criadas utilizando a cláusula `IF NOT EXISTS` para que o script possa ser rodado múltiplas vezes sem quebrar o banco.
3. **Definição das Tabelas:**
    - `outdoors`: `id` (TEXT PK), `nome_identificador` (TEXT), `localizacao_texto` (TEXT), `lat` (REAL), `lng` (REAL), `dimensoes` (TEXT), `especificacoes` (TEXT), `fotos` (TEXT/JSON), `status` (TEXT), `preco_mensal_base` (REAL), `criado_em` (DATETIME), `atualizado_em` (DATETIME).
    - `clientes`: `id` (TEXT PK), `nome_razao_social` (TEXT), `cpf_cnpj` (TEXT UNIQUE), `email` (TEXT UNIQUE), `telefone` (TEXT), `senha_hash` (TEXT), `papel` (TEXT), `criado_em` (DATETIME).
    - `contratos`: `id` (TEXT PK), `cliente_id` (TEXT FK), `outdoor_id` (TEXT FK), `data_inicio` (DATE), `data_teorica_fim` (DATE), `status` (TEXT), `valor_mensal_acordado` (REAL), `criado_em` (DATETIME).
    - `boletos`: `id` (TEXT PK), `contrato_id` (TEXT FK), `mes_referencia` (TEXT), `valor` (REAL), `data_vencimento` (DATE), `status_pagamento` (TEXT), `url_boleto_pdf` (TEXT), `criado_em` (DATETIME).
4. **Relacionamentos:** Habilitar chaves estrangeiras no nível de conexão SQLite (`PRAGMA foreign_keys = ON;`).

## Saídas
- Arquivo `colorsystems.db` inicializado na pasta `.tmp/` contendo todas as 4 tabelas relacionais em estado vazio e prontas para receber dados operacionais.
- Log de sucesso no console (`[SUCESSO] Tabelas criadas.`) ou stack trace formatado com `[ERRO]` em caso de falha.
