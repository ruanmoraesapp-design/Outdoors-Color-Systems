# Constituição do Projeto: gemini.md

## Esquemas de Dados (Schemas)

### 1. `Outdoor` (Produto)
```json
{
  "id": "uuid",
  "nome_identificador": "string",
  "localizacao_texto": "string",
  "bairro": "string",
  "coordenadas_gps": {
    "lat": "number",
    "lng": "number"
  },
  "dimensoes": "string",
  "especificacoes": "string",
  "fotos": ["url_string"],
  "status": "enum('disponivel', 'ocupado', 'manutencao')",
  "preco_mensal_base": "number",
  "criado_em": "timestamp",
  "atualizado_em": "timestamp"
}
```

### 2. `Cliente` (Usuário)
```json
{
  "id": "uuid",
  "nome_razao_social": "string",
  "cpf_cnpj": "string",
  "email": "string",
  "telefone": "string",
  "senha_hash": "string",
  "papel": "enum('cliente', 'admin')",
  "criado_em": "timestamp"
}
```

### 3. `ContratoAluguel` (Transação)
```json
{
  "id": "uuid",
  "cliente_id": "uuid",
  "outdoor_id": "uuid",
  "data_inicio": "date",
  "data_teorica_fim": "date",
  "status": "enum('ativo', 'encerrado', 'inadimplente', 'pendente_aprovacao')",
  "valor_mensal_acordado": "number",
  "criado_em": "timestamp"
}
```

### 4. `BoletoCobranca` (Financeiro)
```json
{
  "id": "uuid",
  "contrato_id": "uuid",
  "mes_referencia": "string (MM/YYYY)",
  "valor": "number",
  "data_vencimento": "date",
  "status_pagamento": "enum('pendente', 'pago', 'atrasado')",
  "url_boleto_pdf": "string",
  "criado_em": "timestamp"
}
```

## Regras de Comportamento
1. **Protocolo B.L.A.S.T.** deve ser seguido rigorosamente.
2. **Arquitetura A.N.T.** (Architecture, Navigation, Tools) é o padrão.
3. Nenhum código em `tools/` até que o Blueprint seja aprovado e o Data Schema definido.
4. `gemini.md` é a *lei*.
5. A interface deve ser moderna, clara e objetiva.
6. **Fluxo de Contratação:** O fechamento de aluguéis não ocorre no sistema; clientes visualizam o catálogo e o botão de contato direciona para o WhatsApp da empresa (89 3422-8275). O sistema gerencia o cliente *após* o fechamento.

## Invariantes Arquiteturais
- Preocupações separadas: Raciocínio na Navegação, SOPs na Arquitetura, Execução nas Ferramentas (Tools).
- Lógica de negócio determinística em scripts Python.
- Implantação baseada primariamente em arquivos locais (SQLite3) provisoriamente, com visão de migrar para Docker/PostgreSQL no futuro.

## Log de Manutenção
- 2026-02-09: Constituição Inicializada em PT-BR.
- 2026-02-28: Esquemas de Dados Base definidos na Fase 1.
