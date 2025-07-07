#!/usr/bin/env python3
"""
Test script to verify stealth browser configuration works with turing.com
"""

import asyncio
from playwright.async_api import async_playwright

async def test_turing_stealth():
    """Test stealth browser configuration against turing.com"""
    print("🎭 Testing stealth browser configuration...")
    
    playwright = await async_playwright().start()
    
    # Enhanced stealth browser configuration to bypass bot detection
    browser = await playwright.chromium.launch(
        headless=False,
        args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-plugins-discovery',
            '--disable-default-apps',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-features=VizDisplayCompositor',
            '--disable-ipc-flooding-protection',
            '--no-first-run',
            '--no-default-browser-check',
            '--no-pings',
            '--password-store=basic',
            '--use-mock-keychain',
            '--window-size=1920,1080'
        ]
    )
    
    # Create context with stealth settings
    context = await browser.new_context(
        user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1920, 'height': 1080},
        extra_http_headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
    )
    
    page = await context.new_page()
    
    # Add stealth JavaScript to hide automation indicators
    await page.add_init_script("""
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Mock languages and plugins
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Hide automation indicators
        window.chrome = {
            runtime: {},
        };
        
        // Mock screen properties
        Object.defineProperty(screen, 'colorDepth', {
            get: () => 24,
        });
        
        Object.defineProperty(screen, 'pixelDepth', {
            get: () => 24,
        });
    """)
    
    try:
        print("🌐 Attempting to navigate to turing.com...")
        await page.goto("https://turing.com", wait_until="domcontentloaded", timeout=30000)
        
        # Wait for page to load
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except:
            await page.wait_for_load_state("load", timeout=10000)
        
        # Check if we successfully loaded the page
        title = await page.title()
        url = page.url
        
        print(f"✅ Successfully navigated to turing.com!")
        print(f"📄 Page title: {title}")
        print(f"🔗 Current URL: {url}")
        
        # Take a screenshot for verification
        await page.screenshot(path="turing_stealth_test.png")
        print("📸 Screenshot saved as turing_stealth_test.png")
        
        # Wait a bit to see the page
        await asyncio.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to navigate to turing.com: {str(e)}")
        return False
        
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    result = asyncio.run(test_turing_stealth())
    if result:
        print("🎉 Stealth configuration successful!")
    else:
        print("💥 Stealth configuration needs improvement")
