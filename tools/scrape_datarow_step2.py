import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False, channel="msedge")
        except Exception:
            browser = await p.chromium.launch(headless=False, channel="chrome")
            
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        await page.goto("https://www.datarow.dev/login")
        
        await page.fill('input[type="email"], input[name="email"], input[name="username"]', 'sabrinaalmondesm@gmail.com')
        await page.fill('input[type="password"], input[name="password"]', '@sabrinacolor')
        await page.click('button[type="submit"]')
        
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        print("Clicando em 'Conjuntos de Dados'...")
        # Clica no botao da sidebar que tem o texto Conjuntos de Dados
        await page.click('button:has-text("Conjuntos de Dados")')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        print("Tirando print da pagina Conjuntos de Dados...")
        os.makedirs('.tmp', exist_ok=True)
        await page.screenshot(path='.tmp/datarow_conjuntos.png')
        
        html = await page.content()
        with open('.tmp/datarow_conjuntos.html', 'w', encoding='utf-8') as f:
            f.write(html)
            
        await browser.close()
        print("Script concluido.")

if __name__ == '__main__':
    asyncio.run(run())
