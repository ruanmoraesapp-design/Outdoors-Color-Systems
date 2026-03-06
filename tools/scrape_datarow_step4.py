import asyncio
from playwright.async_api import async_playwright
import os
import json
import re
import requests

async def download_image(url, dest_path, session_cookies=None):
    """Baixa uma imagem de uma URL e salva localmente."""
    try:
        cookies = {}
        if session_cookies:
            for c in session_cookies:
                cookies[c['name']] = c['value']
        resp = requests.get(url, cookies=cookies, timeout=15)
        if resp.status_code == 200:
            with open(dest_path, 'wb') as f:
                f.write(resp.content)
            return True
    except Exception as e:
        print(f"  > Erro ao baixar imagem {url}: {e}")
    return False

async def run():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False, channel="msedge")
        except Exception:
            browser = await p.chromium.launch(headless=False, channel="chrome")
            
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()
        
        print("Fazendo login...")
        await page.goto("https://www.datarow.dev/login")
        await page.fill('input[type="email"], input[name="email"]', 'sabrinaalmondesm@gmail.com')
        await page.fill('input[type="password"]', '@sabrinacolor')
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(3)
        
        # Navegar para Conjuntos de Dados
        await page.click('button:has-text("Conjuntos de Dados")')
        await asyncio.sleep(2)
        
        # Clicar no dataset "Outdoors"
        print("Clicando no dataset 'Outdoors'...")
        await page.click('text=Outdoors')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(3)
        
        dataset_url = page.url
        print(f"URL do dataset: {dataset_url}")
        await page.screenshot(path='.tmp/dataset_main.png', full_page=True)
        
        # Tentar clicar na tabela de "Controle de Outdoors" ou a primeira tabela disponivel
        print("Listando tabelas disponíveis...")
        tabelas = await page.locator('text=Controle, text=Outdoor, [class*="table-item"], [class*="TableRow"]').all()
        for t in tabelas:
            txt = await t.inner_text()
            print(f"  Tabela encontrada: {txt.strip()[:60]}")
        
        try:
            # Tentar clicar na tabela Controle de Outdoors
            await page.click('text=Controle de Outdoors')
        except:
            # Clicar na primeira tabela disponivel
            await page.locator('table tr:first-child td:first-child, [class*="row"]:first-child').first.click()
        
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(3)
        
        tabela_url = page.url
        print(f"URL da tabela de Outdoors: {tabela_url}")
        await page.screenshot(path='.tmp/tabela_outdoors.png', full_page=True)
        
        # Agora vemos a tabela de outdoors - precisamos extrair linha a linha
        # Primeiro, descobrir quantas linhas existem (ou paginas)
        html = await page.content()
        with open('.tmp/tabela_outdoors.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("Pagina da tabela salva. Extraindo dados das linhas...")
        
        # Clicar na primeira linha para ver os detalhes/atributos
        try:
            rows = await page.locator('tr[class*="row"], tbody tr, [class*="GridRow"], [class*="TableRow"]').all()
            print(f"Total de linhas encontradas: {len(rows)}")
            if rows:
                await rows[0].click()
                await asyncio.sleep(2)
                await page.screenshot(path='.tmp/detalhe_outdoor1.png', full_page=True)
                html_detalhe = await page.content()
                with open('.tmp/detalhe_outdoor1.html', 'w', encoding='utf-8') as f:
                    f.write(html_detalhe)
        except Exception as e:
            print(f"Erro ao clicar na linha: {e}")
        
        await browser.close()
        print("\nPronto! Verifique os arquivos em .tmp/")

if __name__ == '__main__':
    asyncio.run(run())
