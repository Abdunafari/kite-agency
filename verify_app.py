import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Increase timeout for Streamlit to load
        await page.goto("http://localhost:8501", timeout=60000)

        # Wait for the main header to be visible
        await page.wait_for_selector("h1", timeout=10000)

        # Take a screenshot of the dashboard
        await page.screenshot(path="dashboard_sandy_ash.png", full_page=True)
        print("Screenshot saved as dashboard_sandy_ash.png")

        # Fill the form
        await page.fill('textarea[aria-label="Task Details"]', "Test audit for Playwright verification")
        await page.fill('input[aria-label="Budget (KITE)"]', "1.5")

        # Note: Selectbox might be tricky with Streamlit's custom divs, but let's try to just click the button
        # We need a client key to proceed, let's use a dummy one if it validates
        await page.fill('input[aria-label="Client Private Key (to sign Escrow)"]', "0x" + "a"*64)

        # Click the submit button
        await page.click('button:has-text("Deploy Job to Escrow")')

        # Wait for status update
        await asyncio.sleep(2)
        await page.screenshot(path="after_submission.png", full_page=True)
        print("Screenshot after submission saved as after_submission.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
