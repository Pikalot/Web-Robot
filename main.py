from playwright.sync_api import sync_playwright
from llm_model import run_llm_model
import os


def run_test(keyword: str) -> bool:
    """
    Automates a browser search on Amazon using Playwright.

    Args:
        keyword (str): The product name or search term.

    Returns:
        bool: True if the search completes successfully, False otherwise.
    """

    browser_name = os.getenv("BROWSER", "chromium")  # default to chrome if not set
    with sync_playwright() as p:
        browser = getattr(p, browser_name).launch(headless=False)
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
            # search_field = page.get_by_label("Search Amazon")
            search_field = page.locator("#twotabsearchtextbox") # get by ID
            search_field.wait_for(state="visible", timeout=3000)
            
            if not search_field.is_visible():
                raise Exception("Search box not visible")
            
            search_field.fill(keyword)
            print("➡️  Fill search box:", search_field.input_value())
            
            # Click Go button
            page.click("#nav-search-submit-button")
            print("➡️  Click Go button")
            
            # Print results
            print("\n====================================================================")
            page.wait_for_selector('div[role="listitem"][data-index="3"]', timeout=3000)
            try:
                item = page.locator('div[role="listitem"][data-index="3"]')
                title = item.locator("a h2 span").first.inner_text(timeout = 1000)
            except Exception:
                title = None

            try:
                price_item = item.locator("span.a-price span.a-offscreen")
                price_item.wait_for(state="visible", timeout=2000)
                price = price_item.first.inner_text()
            except Exception:
                price = None

            print(f"✅ Success! Product {title if title else 'not'} found")
            print(f"✅ Price: {price if price else 'Price not available'}")
            print("====================================================================\n")
            
            return True # Search successful
       
        except Exception as e:
            print("❌ Error:", e)
            return False # Search failed

def execute(keyword: str, max_entries = 3):
    """
    Repeatedly runs the Amazon search test until success or attempts are exhausted.

    Args:
        keyword (str): The product name or search term to test.
        max_entries (int, optional): Maximum number of retry attempts. Defaults to 3.

    Returns:
        None
    """

    for attempt in range(max_entries):
        print(f"--- Attempt {attempt + 1} of {max_entries} ---")
        success = run_test(keyword)
        if success:
            break

def execute_fixed_model():
    """
    Prompts the user for a search keyword and runs the Amazon search test.
    """
        
    keyword = input("Enter search keyword: ")
    print(f"Searching Amazon for: {keyword}\n")
    execute(keyword)

def execute_llm_model():
    """
    Prompts the user for a search goal and runs the LLM-based automation.

    Asks for a natural language goal (e.g., "find the cheapest blue shirt")
    and passes it to `run_llm_model()` for processing.
    """

    goal = input("Enter search goal (e.g. find the cheapest blue shirt): ")
    run_llm_model(goal)

if __name__ == "__main__":
    """
    Entry point of the program.

    Prompts the user to select between:
    1. The fixed model (manual keyword search)
    2. The LLM model (AI-driven goal-based search)
    """
        
    selecter = input("Select search model (1=Fixed model, 2=LLM): ").strip()
    match selecter: 
        case "1": execute_fixed_model(),
        case "2": execute_llm_model(),
        case _: print("❌ Incorrect selection, terminate program.")
    

