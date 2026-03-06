"""
Script de UPDATE: Adiciona os links do Google Maps coletados pelo robô
diretamente nos registros existentes no banco de dados.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'colorsystems.db')

# Mapa de links extraídos manualmente do terminal do robô
# formato: nome_identificador -> link_google_maps
LINKS_MAPS = {
    "Placa 01": None,  # Link não capturado
    "Placa 02": None,
    "Placa 03": "https://maps.app.goo.gl/roDTYA2hEmzCnVQ17",  # vindo do log
    "Placa 04": None,
    "Placa 05": "https://maps.app.goo.gl/roDTYA2hEmzCnVQ17",
    "Placa 06": "https://maps.app.goo.gl/pobUJYF6PPhzXKyu8",
    "Placa 07": "https://maps.app.goo.gl/3L5Fou2c4kpk3GFTA",
    "Placa 08": "https://maps.app.goo.gl/uSZ85NT5eUdGGQM89",
    "Placa 09": "https://maps.app.goo.gl/K7tAU5aRAUpy6NEFA",
    "Placa 10": "https://maps.app.goo.gl/K1RewsjKEcjC8Ljc7",
    "Placa 11": "https://maps.app.goo.gl/4FNKbTtdg2ssmn3R6",
    "Placa 12": "https://maps.app.goo.gl/XYJBVdnyT5gtxCph7",
    "Placa 13": "https://maps.app.goo.gl/uAf6AFw6LXHSqAQo8",
    "Placa 14": "https://maps.app.goo.gl/uAf6AFw6LXHSqAQo8",
    "Placa 15": "https://maps.app.goo.gl/uAf6AFw6LXHSqAQo8",
    "Placa 16": "https://maps.app.goo.gl/bQKgL3s7a7XWpxgR8",
    "Placa 17": "https://maps.app.goo.gl/wRQzgWEXsKsSMJmu9",
    "Placa 18": "https://maps.app.goo.gl/oFM3CP7yWmaouAjG9",
    "Placa 19": "https://maps.app.goo.gl/gdv2qCKmNn4czLps7",
    "Placa 20": "https://www.google.com/maps?q=-7.0847743,-41.4821036&z=17&hl=pt-BR",
}

STATUS_MAPA = {
    "Placa 01": "ocupado",
    "Placa 02": "ocupado",
    "Placa 03": "disponivel",
    "Placa 04": "ocupado",
    "Placa 05": "ocupado",
    "Placa 06": "disponivel",
    "Placa 07": "ocupado",
    "Placa 08": "ocupado",
    "Placa 09": "ocupado",
    "Placa 10": "ocupado",
    "Placa 11": "ocupado",
    "Placa 12": "ocupado",
    "Placa 13": "ocupado",
    "Placa 14": "ocupado",
    "Placa 15": "ocupado",
    "Placa 16": "ocupado",
    "Placa 17": "ocupado",
    "Placa 18": "ocupado",
    "Placa 19": "ocupado",
    "Placa 20": "ocupado",
}

def update_links():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    atualizados = 0
    for placa, link in LINKS_MAPS.items():
        status_correto = STATUS_MAPA.get(placa, "disponivel")
        cursor.execute(
            '''UPDATE outdoors 
               SET link_google_maps = ?, status = ?, atualizado_em = CURRENT_TIMESTAMP
               WHERE nome_identificador = ?''',
            (link, status_correto, placa)
        )
        if cursor.rowcount > 0:
            print(f"[OK] {placa}: link e status atualizados")
            atualizados += 1
        else:
            print(f"[SKIP] {placa}: nao encontrado no banco")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*40}")
    print(f"UPDATES CONCLUIDOS: {atualizados} / {len(LINKS_MAPS)}")
    print(f"{'='*40}")

if __name__ == '__main__':
    update_links()
