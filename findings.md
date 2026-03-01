# Descobertas & Pesquisa

## Descobertas
1. **Estrela do Norte:** Criar um sistema de gerenciamento completo de aluguéis de outdoors para a empresa *Color Systems*.
2. **Integrações/Infraestrutura:** O sistema usará um banco de dados local (SQLite3) de forma provisória devido a restrições de rede, preparado para migração online (Docker/PostgreSQL) no futuro. Integração com Google Maps para localização e disponibilização de boletos.
3. **Fonte da Verdade:** Banco de dados relacional (SQLite) hospedado na pasta remota/local do projeto (`.tmp/`).
4. **Payload de Entrega:** Aplicação Web completa contendo:
    - **Portal do Cliente (Público):** Catálogo de outdoors com fotos, localização, disponibilidade e especificações. Botão de "Alugar/Contato" que redireciona para o WhatsApp da empresa (89 3422-8275), não havendo fechamento direto na plataforma.
    - **Área do Cliente (Privada):** Login para clientes ativos acompanharem status do aluguel, período de contrato e acessarem boletos de pagamento.
    - **Dashboard Admin (Privado):** Visão geral de outdoors (disponíveis x ocupados), gestão de clientes em contrato, gestão/criação de contratos após fechamento via WhatsApp e controle total do inventário (CRUD de outdoors).
5. **Regras de Comportamento:** Interface clara, moderna e objetiva para facilitar a escolha do cliente e otimizar o gerenciamento pelos administradores.

## Restrições
- Inicialmente local, dependência de Docker.
- Necessita lidar com upload/armazenamento de arquivos (fotos dos outdoors, talvez upload de boletos ou integração bancária automática no futuro).
- **Problema de Rede Local**: O ambiente de rede atual apresenta timeouts (TLS Handshake) massivos ao tentar se comunicar com o Docker Hub e o PyPI. Isso bloqueia a subida do contêiner e a instalação de bibliotecas.

## Recursos
- (Pendente pesquisa de tecnologias ideais).
