import os
import sys

sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys_path not in sys.path:
    sys.path.append(sys_path)

from tools.user_manager import create_user
from tools.outdoor_manager import create_outdoor

def populate_mock_data():
    print("=== Populando Banco de Dados com Dados Fictícios ===")
    
    # 1. Usuários de Teste
    print("\n--- Criando Usuários ---")
    admin_id = create_user(
        nome_razao_social="Admin Color Systems",
        cpf_cnpj="000.000.000-00",
        email="admin@colorsystems.com",
        telefone="89999999999",
        senha_plana="admin123",
        papel="admin"
    )
    print(f"Admin criado com ID: {admin_id}")
    
    cliente_id = create_user(
        nome_razao_social="Cliente Teste SA",
        cpf_cnpj="111.111.111-11",
        email="cliente@teste.com",
        telefone="89888888888",
        senha_plana="cliente123",
        papel="cliente"
    )
    print(f"Cliente criado com ID: {cliente_id}")

    # 2. Outdoors de Teste
    print("\n--- Criando Outdoors ---")
    outdoors_data = [
        {
            "nome": "Painel Luminoso Centro",
            "localizacao": "Praça Central - Em frente ao Banco Principal",
            "preco": 1200.00,
            "status": "disponivel",
            "lat": -6.65,
            "lng": -50.2,
            "dimensoes": "9x3",
            "especificacoes": "Painel Front Light em estrutura galvanizada. Excelente fluxo de pedestres e veículos.",
            "fotos": '["https://maps.app.goo.gl/XXXXX"]'
        },
        {
            "nome": "Outdoor Duplo BR-316",
            "localizacao": "Rodovia BR-316, Km 5 - Picos-PI (Link Google Maps na foto)",
            "preco": 2500.00,
            "status": "disponivel",
            "lat": -7.0,
            "lng": -41.4,
            "dimensoes": "18x3",
            "especificacoes": "Visibilidade de mais de 1km na rodovia principal.",
            "fotos": '["https://maps.app.goo.gl/gQXXXX"]'
        },
        {
            "nome": "Empena Cega Shopping",
            "localizacao": "Avenida Brasil, Lateral do Shopping",
            "preco": 3000.00,
            "status": "ocupado",
            "lat": -8.0,
            "lng": -40.0,
            "dimensoes": "6x12",
            "especificacoes": "Altíssima retenção visual no cruzamento de maior fluxo da zona leste.",
            "fotos": '["https://maps.app.goo.gl/YYYYY"]'
        },
        {
            "nome": "Mega Painel Cruzamento",
            "localizacao": "Rotatória do Mercado Municipal - Av. São Sebastião",
            "preco": 900.00,
            "status": "disponivel",
            "lat": -5.0,
            "lng": -42.8,
            "dimensoes": "9x3",
            "especificacoes": "Fluxo viário constante os 7 dias da semana.",
            "fotos": '["https://maps.app.goo.gl/ZZZZZ"]'
        },
        {
            "nome": "LED Screen Premium",
            "localizacao": "Principal Avenida de Bares e Restaurantes",
            "preco": 1800.00,
            "status": "disponivel",
            "lat": -6.0,
            "lng": -41.0,
            "dimensoes": "4x2",
            "especificacoes": "Super telão de LED de alta resolução. Loops de 10s.",
            "fotos": '["https://maps.app.goo.gl/WWWWW"]'
        }
    ]

    for data in outdoors_data:
        oid = create_outdoor(**data)
        print(f"Outdoor '{data['nome']}' processado. ID: {oid}")
        
    print("\n[SUCESSO] Todos os dados fictícios foram gerados.")

if __name__ == "__main__":
    populate_mock_data()
