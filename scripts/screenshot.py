"""헤드리스 브라우저로 각 시점 스크린샷을 찍어 결과를 눈으로 확인하는 스크립트.
사용: pip install playwright && playwright install chromium
      python scripts/screenshot.py            # 기본 시점 전부
      python scripts/screenshot.py orbit walk # 원하는 시점만
결과: shots/<시점>.png
WebGL이 GPU 없이 돌면 매우 느려서(1~2fps) 시점마다 몇 초씩 기다립니다.
"""
import asyncio, sys, subprocess, time, os, pathlib
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
VIEWS = sys.argv[1:] or ['walk', 'entrance', 'performer', 'audience', 'orbit']
async def main():
    os.makedirs(ROOT / 'shots', exist_ok=True)
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8765', '-d', str(ROOT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
            pg = await b.new_page(viewport={'width': 960, 'height': 600})
            await pg.add_init_script("window.__noAuto=true")   # 느린 환경에서 자동 화질 저하 끄기
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.on('response', lambda r: errs.append(f'{r.status} {r.url}') if r.status >= 400 and not r.url.endswith('favicon.ico') else None)
            await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(9000)
            for v in VIEWS:
                await pg.evaluate(f"document.querySelector('[data-view={v}]').click()")
                await pg.wait_for_timeout(4000)
                await pg.screenshot(path=str(ROOT / 'shots' / f'{v}.png'))
            print('\n'.join(errs) or 'no errors')
            await b.close()
    finally:
        srv.terminate()
asyncio.run(main())
