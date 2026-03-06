import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        # Tenta usar o Edge ou Chrome local para pular o download gigabyte do Chromium
        try:
            browser = await p.chromium.launch(headless=False, channel="msedge")
            print("Navegador (Edge) iniciado.")
        except Exception:
            try:
                browser = await p.chromium.launch(headless=False, channel="chrome")
                print("Navegador (Chrome) iniciado.")
            except Exception as e:
                print(f"Erro ao abrir navegador: {e}")
                return
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        print("Acessando a pagina de login do Datarow...")
        await page.goto("https://www.datarow.dev/login")
        
        # Preencher credenciais
        print("Realizando login...")
        await page.fill('input[type="email"], input[name="email"], input[name="username"]', 'sabrinaalmondesm@gmail.com')
        await page.fill('input[type="password"], input[name="password"]', '@sabrinacolor')
        
        # Clicar no botao de login (precisamos usar um seletor abrangente)
        await page.click('button[type="submit"]')
        
        # Espera pela navegacao pos login
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(3) # tempo extra de seguranca
        
        print("Tirando print da pagina logada...")
        os.makedirs('.tmp', exist_ok=True)
        await page.screenshot(path='.tmp/datarow_dashboard.png')
        
        # Salvando HTML pra eu ensinar o robo a ler
        html = await page.content()
        with open('.tmp/datarow_dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html)
            
        print("Navegando ate o Controle de Outdoors (tentativa manual ou via menu)...")
        # Vamos procurar um link com texto parecido com "Outdoors" ou "Paineis"
        links = await page.locator('a').all()
        outdoor_url = None
        for link in links:
            text = await link.inner_text()
            href = await link.get_attribute('href')
            if text and ('outdoor' in text.lower() or 'pain' in text.lower() or 'ponto' in text.lower()) and href:
                outdoor_url = href
                print(f"Descobri a URL dos outdoors: {outdoor_url}")
                break
                
        if outdoor_url:
            base_url = "https://www.datarow.dev"
            if not outdoor_url.startswith('http'):
                outdoor_url = base_url + outdoor_url
                
            await page.goto(outdoor_url)
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            print("Tirando print da lista de outdoors...")
            await page.screenshot(path='.tmp/datarow_outdoors_list.png', full_page=True)
            
            html2 = await page.content()
            with open('.tmp/datarow_outdoors_list.html', 'w', encoding='utf-8') as f:
                f.write(html2)
                
        else:
            print("Aviso: Nao consegui clicar no link direto dos outdoors, precisamos analisar o Menu no HTML gerado.")
            
        await browser.close()
        print("Script finalizado. Arquivos salvos na pasta .tmp")

if __name__ == '__main__':
    asyncio.run(run())
