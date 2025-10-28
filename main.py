from playwright.sync_api import sync_playwright

def run_test(keyword: str) -> bool:
    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=False)
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Go to Amazon
            page.goto("https://www.amazon.com/")
            print("➡️  Go to page title:", page.title())
            
            # Click on continue if Amazon prompts for new user
            cont_button = page.get_by_role("button", name = "Continue Shopping")
            if cont_button.is_visible():
                cont_button.click()

            # Fill in search box
            # search_field = page.get_by_role("searchbox", name = "Search Amazon")            
            search_field = page.get_by_label("Search Amazon")
            # search_field = page.locator("#twotabsearchtextbox") # get by ID
            search_field.wait_for(state="visible", timeout=3000)
            
            if not search_field.is_visible():
                raise Exception("Search box not visible")
            
            search_field.fill(keyword)
            print("➡️  Fill search box:", search_field.input_value())
            
            # Click Go button
            page.click("#nav-search-submit-button")
            print("➡️  Click Go button")
            print("====================================================================")

            # Find the first product result, print title and price
            # page.wait_for_selector("div[data-component-type='s-search-result']", timeout=10000)
            page.wait_for_selector('div[role="listitem"][data-index="3"]', timeout=3000)
            item = page.locator('div[role="listitem"][data-index="3"]')
            title = item.locator("a h2 span").first.inner_text()
            price = item.locator("span.a-price span.a-offscreen").first.inner_text()
            print(f"✅ Success! Product {title} found")
            print(f"✅ Price: {price}")
            print("====================================================================\n")
            
            return True # Search successful
       
        except Exception as e:
            print("❌ Error:", e)
            return False # Search failed

def execute(keyword: str, max_entries = 3):
    for attempt in range(max_entries):
        print(f"--- Attempt {attempt + 1} of {max_entries} ---")
        success = run_test(keyword)

        if success:
            break

if __name__ == "__main__":
    keyword = input("Enter search keyword: ")
    print(f"Searching Amazon for: {keyword}\n")
    execute(keyword, 5)