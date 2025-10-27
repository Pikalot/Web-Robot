from playwright.sync_api import sync_playwright

def execute():
    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=False)
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        
        # Go to Amazon
        page.goto("https://www.amazon.com/")
        print("✅ Go to page title:", page.title())
        
        # Click on continue if Amazon prompts for new user
        cont_button = page.get_by_role("button", name = "Continue Shopping")
        if cont_button.is_visible():
            cont_button.click()

        search_field = page.get_by_role("searchbox", name = "Search Amazon")
        search_field.fill("blue shirt")
        print("✅ Fill search box:", search_field.input_value())
        # go_button = page.get_by_role("button", name = "Go")
        # print(go_button)
        # go_button.click()
        # search_field.press()
        
        browser.close()

if __name__ == "__main__":
    execute()