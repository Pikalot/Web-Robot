from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import openai, json, os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def get_page_context(page) -> dict:
    return {
        "url": page.url,
        "title": page.title(),
        "elements": [
            {"role": "searchbox", "id": "twotabsearchtextbox"},
            {"role": "button", "id": "nav-search-submit-button", "name": "Go"},
            {
                "role": "combobox",
                "label": "Sort by:",
                "id": "s-result-sort-select",
                "options": [
                    {"label": "Featured", "value": "relevanceblender"},
                    {"label": "Price: Low to High", "value": "price-asc-rank"},
                    {"label": "Price: High to Low", "value": "price-desc-rank"},
                    {"label": "Avg. Customer Review", "value": "review-rank"},
                    {"label": "Newest Arrivals", "value": "date-desc-rank"},
                    {"label": "Best Sellers", "value": "exact-aware-popularity-rank"},
                ],
            },
        ],
    }

def ask_llm_for_plan(goal, context) -> list[dict]:
    prompt = f"""
    You are a Playwright automation planner — not a programmer.
    Your job is ONLY to output a minimal JSON plan of steps for the Playwright driver to execute.

    Rules:
    - Return ONLY valid JSON.
    - Use the element roles or selectors provided in Page context.
    - Do NOT write JavaScript or code.
    - Each step must include: "action" (fill, click, select_option, wait_for_selector), and the "selector" or "role".
    - If sorting is needed, use the combobox options by their 'value' attributes.
    - Return a JSON object with a key "plan" whose value is a list of steps.
 
    Goal: {goal}
    Page context: {json.dumps(context)}

    Example output:
    [
      {{"action": "fill", "selector": "#twotabsearchtextbox", "value": "blue shirt"}},
      {{"action": "click", "selector": "#nav-search-submit-button"}},
      {{"action": "select_option", "selector": "#s-result-sort-select", "value": "price-asc-rank"}}
    ]
    """
    res = openai.chat.completions.create(
      model="gpt-4o",
      response_format={"type": "json_object"},
      messages=[{"role": "user", "content": prompt}],
    )
    data = json.loads(res.choices[0].message.content)
    plan = data.get("plan") or data  
    if not isinstance(plan, list):
        raise ValueError(f"Unexpected JSON: {data}")

    # print(plan)
    return plan

def run_llm_model(goal: str):
    browser_name = os.getenv("BROWSER", "chromium")  # default to chrome if not set

    with sync_playwright() as p:
      # browser = p.firefox.launch(headless=False)
      browser = getattr(p, browser_name).launch(headless=False)
      page = browser.new_page()
      
      page.goto("https://www.amazon.com/")
      print("➡️  Page title:", page.title())

      # Click on continue if Amazon prompts for new user
      cont_button = page.get_by_role("button", name = "Continue Shopping")
      if cont_button.is_visible():
        cont_button.click()

      context = get_page_context(page)
      plan = ask_llm_for_plan(goal, context)
      page.wait_for_timeout(4000)  # small pause between actions

      try:
        for step in plan:
          action = step["action"]
          print(f"➡️  Executing: {action} -> {step}")

          if action == "fill":
            searchfield = page.locator(step["selector"])
            searchfield.wait_for(state="visible", timeout=3000)
            searchfield.fill(step["value"])
          elif action == "click":
              if "selector" in step:
                  page.click(step["selector"])
              elif "role" in step:
                locator = page.get_by_role(step["role"], name=step["name"])
                print(f"➡️  Clicking element with role: {step['role']} and name: {step['name']}", locator)
                locator.await_for(state="visible", timeout=3000)
                locator.click()
          elif action == "wait_for":
            page.wait_for_selector(step["selector"])
          elif action == "select_option":
            # Wait for dropdown to be ready
            dropdown = page.locator("#s-result-sort-select")
            dropdown.wait_for(state="visible")
            # Mini pause to ensure dropdown is ready
            page.wait_for_timeout(1000)
            dropdown.focus()
            page.keyboard.press("Enter")      
            page.select_option(step["selector"], step["value"])
            page.wait_for_timeout(1000)

        # Print the product name and price if available
        print("\n====================================================================")
        try:
          page.wait_for_selector('div[role="listitem"][data-index="3"]', timeout=1000)
          item = page.locator('div[role="listitem"][data-index="3"]')
          title = item.locator("a h2 span").first.inner_text(timeout = 1000)
        except Exception:
            title = None
            print("❌ Error: Could not find product title.")

        try:
            price_item = item.locator("span.a-price span.a-offscreen")
            price_item.wait_for(state="visible", timeout=1000)
            price = price_item.first.inner_text()
        except Exception:
            price = None

        if title:
           print(f"✅ Success! Product {title} found")
        print(f"✅ Price: {price if price else 'Price not available'}")
        print("====================================================================\n")
              
        print("✅ LLM model finished.")
        browser.close()
      
      except Exception as e:
        print("❌ Error during plan execution:", e)
        browser.close()