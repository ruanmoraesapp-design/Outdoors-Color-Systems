import asyncio
from playwright.async_api import async_playwright
import os
import json
import re

async def run():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False, channel="msedge")
        except Exception:
            browser = await p.chromium.launch(headless=False, channel="chrome")
            
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()
        
        await page.goto("https://www.datarow.dev/login")
        await page.fill('input[type="email"], input[name="email"]', 'sabrinaalmondesm@gmail.com')
        await page.fill('input[type="password"]', '@sabrinacolor')
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(3)
        
        print(f"URL apos login: {page.url}")
        
        # Clicar em Conjuntos de Dados no menu lateral
        await page.click('button:has-text("Conjuntos de Dados")')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(3)
        
        print(f"URL apos clicar Conjuntos de Dados: {page.url}")
        
        # Agora encontrar o card de "Controle de Outdoors" e clicar nele
        # No Datarow, os datasets aparecem como cards com nome
        print("Procurando card 'Controle de Outdoors'...")
        
        # Primeiro vamos salvar o screenshot para debug
        await page.screenshot(path='.tmp/conjuntos_dados.png', full_page=True)
        
        # Tentar clicar no texto que contém "Controle" ou "Outdoor"
        try:
            await page.click('text=Controle de Outdoors')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
        except:
            print("Tentando locator alternativo...")
            await page.click('[class*="card"]:has-text("Outdoor"), [class*="Card"]:has-text("Outdoor"), div:has-text("Controle de Outdoors")')
            await asyncio.sleep(3)
        
        url_dataset = page.url
        print(f"URL do dataset de Outdoors: {url_dataset}")
        
        os.makedirs('.tmp', exist_ok=True)
        await page.screenshot(path='.tmp/dataset_outdoors.png', full_page=True)
        
        # Pegar o ID do dataset da URL (ex: /dataset/abc123)
        match = re.search(r'/(\w{8}-\w{4}-\w{4}-\w{4}-\w{12}|\w+)$', url_dataset)
        if match:
            dataset_id = match.group(1)
            print(f"ID do dataset: {dataset_id}")
            with open('.tmp/dataset_id.txt', 'w') as f:
                f.write(dataset_id)
        
        # Agora vamos descobrir quais tabelas existem dentro desse dataset
        # Geralmente há uma aba de tabelas ou lista
        html = await page.content()
        with open('.tmp/dataset_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Tentar clicar na tabela de Outdoors (que é a lista de paineis)
        try:
            # Procura por texto de tabela dentro do dataset
            all_texts = await page.locator('button, a, [role="button"], [class*="table"], [class*="TableItem"]').all()
            print("---- Itens clicáveis na página ----")
            for el in all_texts[:20]:
                try:
                    t = await el.inner_text()
                    if t.strip():
                        print(f"  > '{t.strip()[:60]}'")
                except:
                    pass
        except Exception as e:
            print(f"Erro ao listar itens: {e}")
        
        await browser.close()
        print("Pronto! Analise .tmp/dataset_outdoors.png e .tmp/dataset_page.html")

if __name__ == '__main__':
    asyncio.run(run())
