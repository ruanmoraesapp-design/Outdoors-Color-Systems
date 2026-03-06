"""
EXTRATOR FINAL do Datarow - Versao 2
Objetivo: Iterar pelas 3 paginas da tabela "Controle de Outdoors" e 
coletar: Id, Endereco, Material, Dimensoes, Status, Cliente, 
Foto URL, Data Inicio, Data Fim, Link Google Maps
Ao final, salva em tools/mock_datarow_v2.json e executa a importacao.
"""
import asyncio
from playwright.async_api import async_playwright
import os
import json
import re

BASE_URL = "https://www.datarow.dev"
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), 'mock_datarow_v2.json')

async def run():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False, channel="msedge")
        except Exception:
            browser = await p.chromium.launch(headless=False, channel="chrome")
            
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()
        
        # ---- LOGIN ----
        print("Fazendo login no Datarow...")
        await page.goto(f"{BASE_URL}/login")
        await page.fill('input[type="email"]', 'sabrinaalmondesm@gmail.com')
        await page.fill('input[type="password"]', '@sabrinacolor')
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(3)
        
        # ---- NAVEGAR ATE A TABELA ----
        print("Navegando para Conjuntos de Dados > Outdoors > Controle de Outdoors...")
        await page.click('button:has-text("Conjuntos de Dados")')
        await asyncio.sleep(2)
        await page.click('text=Outdoors')
        await asyncio.sleep(3)
        
        # Agora devemos estar na pagina do dataset Outdoors, que mostra as tabelas
        # Clicar em "Controle de Outdoors" (primeira tabela)
        try:
            await page.click('text=Controle de Outdoors')
            await asyncio.sleep(3)
        except:
            print("Clique em 'Controle de Outdoors' falhou, tentando link alternativo...")
        
        print(f"URL atual: {page.url}")
        await page.screenshot(path='.tmp/step_tabela.png')
        
        all_records = []
        total_paginas = 3  # Vimos que sao 3 paginas
        
        for pagina in range(1, total_paginas + 1):
            print(f"\n{'='*50}")
            print(f"  PAGINA {pagina} de {total_paginas}")
            print(f"{'='*50}")
            
            # Aguarda as linhas carregarem
            await asyncio.sleep(2)
            
            # Pegar todas as linhas da tabela (tr na tbody)
            rows = await page.locator('tbody tr').all()
            print(f"Linhas encontradas nesta pagina: {len(rows)}")
            
            # Para cada linha, vamos extrair os dados da tabela e depois abrir o formulario
            for i, row in enumerate(rows):
                try:
                    cells = await row.locator('td').all()
                    
                    # Extrair celulas visiveis da tabela (Id, Tipo, Endereco, Localizacao, Material, Dimensoes...)
                    cell_texts = []
                    for cell in cells:
                        t = await cell.inner_text()
                        cell_texts.append(t.strip())
                    
                    # Tentar pegar link do Google Maps na coluna Localizacao
                    link_maps = None
                    try:
                        link_el = await row.locator('a[href*="maps"], a[href*="google"]').first.get_attribute('href')
                        link_maps = link_el
                    except:
                        pass
                    
                    print(f"[{i+1}] Dados da linha: {cell_texts[:7]}")
                    
                    # Agora clicar na linha para abrir o formulario de detalhes
                    await row.click()
                    await asyncio.sleep(2)
                    
                    # O formulario ou modal de detalhes deve estar aberto
                    # Tentar capturar os campos extras (Fotos, Status, Cliente, Datas)
                    foto_url = None
                    data_inicio = None
                    data_fim = None
                    cliente_nome = None
                    status_val = None
                    
                    try:
                        # Tirar screenshot do modal/detalhe
                        await page.screenshot(path=f'.tmp/detalhe_p{pagina}_r{i+1}.png')
                        
                        # Buscar imagens no modal que foi aberto
                        img_els = await page.locator('[class*="modal"] img, [class*="Modal"] img, [class*="detail"] img, [class*="form"] img, [role="dialog"] img').all()
                        if not img_els:
                            # Tentar pegar qualquer img que nao seja logo
                            img_els = await page.locator('img[src*="supabase"], img[src*="storage"], img[src*="upload"]').all()
                        
                        for img in img_els:
                            src = await img.get_attribute('src')
                            if src and 'logo' not in src and 'icon' not in src:
                                foto_url = src
                                print(f"  > Foto encontrada: {src[:80]}...")
                                break
                        
                        # Buscar campos de texto com datas e cliente
                        # No Datarow, os campos ficam em inputs do formulario
                        inputs = await page.locator('[class*="modal"] input, [class*="modal"] textarea, [role="dialog"] input, [role="dialog"] [class*="field"]').all()
                        for inp in inputs:
                            label_el = await page.locator(f'label[for="{await inp.get_attribute("id")}"]').all()
                            label = ""
                            if label_el:
                                label = (await label_el[0].inner_text()).lower()
                            val = await inp.input_value() if await inp.get_attribute('type') != 'checkbox' else ""
                            
                            if 'inicio' in label or 'start' in label or 'inicio' in (await inp.get_attribute('placeholder') or '').lower():
                                data_inicio = val
                            elif 'fim' in label or 'end' in label or 'validade' in label or 'venc' in label:
                                data_fim = val
                            elif 'cliente' in label or 'client' in label or 'locatario' in label:
                                cliente_nome = val
                            elif 'status' in label:
                                status_val = val
                        
                        # Alternativa: ler todos os textos do modal/dialog
                        if not cliente_nome:
                            dialog_texts = await page.locator('[role="dialog"], [class*="Modal"], [class*="modal"]').first.inner_text()
                            print(f"  > Conteudo do dialog (primeiros 300ch): {dialog_texts[:300]}")
                        
                    except Exception as e:
                        print(f"  > Erro ao extrair detalhe: {e}")
                    
                    # Fechar o modal/formulario (ESC ou botao fechar)
                    try:
                        await page.keyboard.press('Escape')
                        await asyncio.sleep(1)
                    except:
                        pass
                    
                    # Construir o record com dados combinados da tabela + formulario
                    record = {
                        "id": cell_texts[1] if len(cell_texts) > 1 else f"Placa {i+1:02d}",
                        "tipo": cell_texts[2] if len(cell_texts) > 2 else "Outdoor",
                        "endereco": cell_texts[3] if len(cell_texts) > 3 else "",
                        "link_google_maps": link_maps,
                        "material": cell_texts[5] if len(cell_texts) > 5 else "",
                        "dimensoes": cell_texts[6] if len(cell_texts) > 6 else "9x3m",
                        "foto_url": foto_url,
                        "data_inicio": data_inicio,
                        "data_fim": data_fim,
                        "cliente": cliente_nome,
                        "status": status_val or ("ocupado" if len(cell_texts) > 4 and "vermelho" in str(cells) else "disponivel"),
                    }
                    all_records.append(record)
                    print(f"  > Record adicionado: {record['id']} - {record['endereco'][:40]}")
                    
                except Exception as e:
                    print(f"  > ERRO na linha {i+1}: {e}")
                    continue
            
            # Passar para a proxima pagina
            if pagina < total_paginas:
                print(f"\nPassando para a pagina {pagina + 1}...")
                try:
                    # Clicar no botao proximo (seta direita na paginacao)
                    next_btn = page.locator('button[aria-label*="next"], button[aria-label*="proxima"], button:has(svg.ph-arrow-right), [class*="pagination"] button:last-child')
                    await next_btn.last.click()
                    await asyncio.sleep(3)
                except Exception as e:
                    print(f"  Erro ao passar de pagina: {e}")
                    # Tentar clicar na seta de paginacao pelo screenshot
                    try:
                        # Botao de proxima pagina fica no canto inferior direito
                        await page.locator('button svg').last.click()
                        await asyncio.sleep(3)
                    except:
                        break
        
        await browser.close()
        
        # Salvar JSON
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(all_records, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*50}")
        print(f"EXTRACAO CONCLUIDA!")
        print(f"Total de records extraidos: {len(all_records)}")
        print(f"Arquivo salvo em: {OUTPUT_JSON}")
        print(f"{'='*50}")

if __name__ == '__main__':
    asyncio.run(run())
