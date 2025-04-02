from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.interpark.com')
    # 수동 로그인 후 context.storage_state()로 세션 저장 가능
    browser.close()
