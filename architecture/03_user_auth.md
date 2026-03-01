# SOP 03: Gestão de Usuários (Clientes e Autenticação)

## Objetivo
Criar os procedimentos operacionais para gerenciar o registro de novos administradores e clientes base da plataforma, garantindo o hash seguro das senhas e controle baseado em papéis (RBAC).

## Camada de Navegação (Inputs Esperados)
O arquivo `tools/user_manager.py` pode ser importado para registro e validação de login, ou executado no terminal para provisionar usuários iniciais.

## Lógica de Execução (Regras)

### 1. Criar Usuário (Cadastro Base)
**Requisitos:**
- `nome_razao_social`, `cpf_cnpj`, `email`, `senha_plana`, `papel`.
- O papel (`papel`) só aceita `'cliente'` ou `'admin'`.
- Campos formatados e dados sensíveis protegidos (hash da `senha_plana`).
- `cpf_cnpj` e `email` devem ser únicos (o DB já impõe UNIQUE Constraint). Usar tratamento de erro (IntegrityError) se houver duplicação.

**Processamento:**
- Gerar UUID e criptografar a senha utilizando a biblioteca `werkzeug.security` (Padrão para bcrypt/pbkdf2 em apps web simples) ou `hashlib` se não quisermos depender de bibliotecas externas grandes neste momento (Usaremos `hashlib` com `os.urandom` (salt) provisoriamente para evitar dependências adicionais).
- Inserir na tabela `clientes`.

### 2. Validação de Login (Authenticate)
**Requisitos:**
- `email` e `senha_plana`.

**Processamento:**
- Buscar o usuário via `email`.
- Verificar se a `senha_plana` enviada, quando processada contra a `senha_hash` armazenada no DB, confere.
- Retornar True e os dados do usuário (exceto password) se logado com sucesso, ou False caso e-mail ou senha estejam incorretos.

### 3. Leitura e Atualização (Opcional por agora)
- Listar clientes: Usado no Dashboard pelo administrador.

## Saídas
- Confirmação de cadastro do usuário.
- Confirmação booleana ao tentar fazer login.
