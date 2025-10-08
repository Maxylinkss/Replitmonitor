import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

REPLIT_URL = os.environ.get('REPLIT_URL', 'https://replit.com/@yourusername/yourrepl')
COOKIES_JSON = os.environ.get('COOKIES_JSON', '[]')
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', '30'))

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def load_cookies(driver):
    try:
        cookies = json.loads(COOKIES_JSON)
        driver.get(REPLIT_URL)
        time.sleep(2)
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Error adding cookie: {e}")
        driver.refresh()
        time.sleep(3)
        print("✓ Cookies loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Error loading cookies: {e}")
        return False

def check_and_restart(driver):
    try:
        run_button_selectors = [
            "//button[contains(text(), 'Run')]",
            "//button[@aria-label='Run']",
            "//button[contains(@class, 'run-button')]",
            "//*[contains(text(), 'Run') and contains(@role, 'button')]"
        ]
        for selector in run_button_selectors:
            try:
                run_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                if run_button.is_displayed():
                    print("⚠ Repl is stopped! Clicking Run button...")
                    run_button.click()
                    print("✓ Run button clicked successfully")
                    time.sleep(5)
                    return True
            except (TimeoutException, NoSuchElementException):
                continue
        print("✓ Repl is running")
        return False
    except Exception as e:
        print(f"✗ Error checking Repl status: {e}")
        return False

def monitor_repl():
    print("=" * 50)
    print("Starting Replit Auto-Restarter")
    print(f"Monitoring: {REPLIT_URL}")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("=" * 50)
    driver = None
    restart_count = 0
    try:
        driver = setup_driver()
        print("✓ Chrome driver initialized")
        if not load_cookies(driver):
            print("✗ Failed to load cookies. Please check COOKIES_JSON environment variable")
            return
        driver.get(REPLIT_URL)
        time.sleep(5)
        while True:
            try:
                print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking Repl status...")
                if check_and_restart(driver):
                    restart_count += 1
                    print(f"Total restarts: {restart_count}")
                time.sleep(CHECK_INTERVAL)
            except Exception as e:
                print(f"✗ Error in monitoring loop: {e}")
                print("Attempting to recover...")
                try:
                    driver.refresh()
                    time.sleep(5)
                except:
                    print("Recovery failed. Reinitializing driver...")
                    driver.quit()
                    driver = setup_driver()
                    load_cookies(driver)
                    driver.get(REPLIT_URL)
                    time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nStopping monitor...")
    except Exception as e:
        print(f"✗ Fatal error: {e}")
    finally:
        if driver:
            driver.quit()
            print("✓ Driver closed")

if __name__ == "__main__":
    monitor_repl()
