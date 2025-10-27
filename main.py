from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)
    page = browser.new_page()
    page.goto("https://tuananh-hub.vercel.app/")
    print("✅ Page title:", page.title())
    browser.close()
