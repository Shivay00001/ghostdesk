import logging
import asyncio
import threading
from typing import List, Any
from playwright.sync_api import sync_playwright
from .base import BaseSkill, SkillResult

logger = logging.getLogger(__name__)

class BrowserSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="Browser",
            description="Web browsing capabilities using Playwright"
        )
        self.headless = False # Visible browser for "Ghost" effect

    @property
    def actions(self) -> List[str]:
        return ["BROWSE_OPEN", "BROWSE_GOTO", "BROWSE_READ", "BROWSE_CLOSE"]

    def _run_sync(self, func, *args):
        # Playwright sync API is blocking, so we run it directly.
        # Ideally, we should reuse a browser instance.
        # For this PoC, we might spin up a context or use a persistent one if possible.
        # But 'sync_playwright' context manager closes on exit.
        # We need a persistent browser session.
        pass

    def execute(self, action: str, params: Any, context: Any = None) -> SkillResult:
        try:
            # Note: Managing persistent browser state in sync mode is tricky without a dedicated thread loop.
            # We will launch a fresh instance for each atomic "Task session" or just one-off actions for now.
            # For a true agent, we'd want a persistent browser. 
            # Let's implement a simple "One-Shot" browse for READ, and OPEN for just launching.
            
            if action == "BROWSE_OPEN":
                # Just launch and keep open? Tough with sync manager.
                # We'll use a thread to keep it alive? Or just use subprocess for "Open"?
                # If we want to CONTROL it, we need to keep the handle.
                return SkillResult(success=True, message="Browser session started (Mock - Persistent session TODO)")

            if action == "BROWSE_GOTO" or action == "BROWSE_READ":
                url = str(params)
                if not url.startswith("http"):
                    url = "https://" + url
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=self.headless)
                    page = browser.new_page()
                    page.goto(url)
                    
                    if action == "BROWSE_READ":
                        title = page.title()
                        content = page.inner_text("body")[:1000] # First 1000 chars
                        browser.close()
                        return SkillResult(success=True, message=f"Read {title}: {content}...")
                    
                    # BROWSE_GOTO just goes there.
                    # If we close browser, it's gone.
                    # For PoC, we wait a bit then close?
                    page.wait_for_timeout(5000)
                    browser.close()
                    return SkillResult(success=True, message=f"Visited {url}")

            return SkillResult(success=False, message=f"Action {action} not supported")

        except Exception as e:
            return SkillResult(success=False, message=str(e))
