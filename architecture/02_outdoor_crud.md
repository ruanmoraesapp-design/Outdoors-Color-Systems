# SOP 02: CRUD de Outdoors

## Objetivo
Definir o procedimento padronizado para Criar, Ler, Atualizar e Deletar (CRUD) registros na tabela `outdoors` de forma segura, mantendo a integridade referencial.

## Camada de Navegação (Inputs Esperados)
O arquivo `tools/outdoor_manager.py` deve agir como um módulo importável ou invocável via CLI passando o comando desejado (`create`, `read`, `update`, `delete`) e os argumentos.

## Lógica de Execução (Regras)

### 1. Criar (Create)
**Requisitos:**
- `nome_identificador` (obrigatório, string).
- `localizacao_texto` (obrigatório, string).
- `status` (obrigatório, restrito a 'disponivel', 'ocupado', 'manutencao').
- `preco_mensal_base` (obrigatório, numérico).
- `lat`, `lng` (opcionais, porém recomendados).
- `dimensoes`, `especificacoes` (opcionais).
- O `id` do outdoor DEVE ser gerado via UUID (v4) programaticamente no ato da criação.
- `fotos` (JSON string, array vazio `[]` por padrão se não fornecido).

**Processamento:**
- Inserir na tabela `outdoors`. Retornar sucesso e o UUID gerado.

### 2. Ler (Read)
**Requisitos:**
- Permitir listagem total (para o Dashboard Admin/Catálogo).
- Permitir busca por ID específico.
- Permitir filtro por `status` (ex: apenas `disponivel` para a vitrine do cliente).

**Processamento:**
- Executar `SELECT` com parâmetros de filtro opcionais. Retornar os dados estruturados como lista de dicionários.

### 3. Atualizar (Update)
**Requisitos:**
- `id` (obrigatório para localizar o registro).
- Campos que serão atualizados (ex: alteração de status para 'ocupado' ou edição de preço).
- O timestamp `atualizado_em` deve ser forçado com a data e hora atual no momento do update.

### 4. Deletar (Delete)
**Requisitos:**
- `id` (obrigatório).
**Regras de Dependência:**
- O SQLite deve impedir a deleção (RESTRICT) caso existam contratos ativos atrelados a este outdoor. Tratar a exceção de integridade referencial devolvendo `[ERRO] Não é possível deletar outdoor que possui contratos registrados. Mude o status para 'manutencao'.`

## Saídas
- Sucesso: Confirmação da operação.
- Falha: Exibição descritiva do erro (SQLite Integrity Error, tipagem incorreta, etc.).
