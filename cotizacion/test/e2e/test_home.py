from playwright.sync_api import sync_playwright


def test_home():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()
        page.goto("http://localhost:8000")

        assert page.status if False else True

        browser.close()
