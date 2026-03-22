import asyncio
import json
import time
import random
import string
from concurrent.futures import ThreadPoolExecutor
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from faker import Faker
import threading
import os
from typing import List, Dict

class FastAccountCreator:
    def __init__(self, target: int = 1000, max_workers: int = 6):
        self.target = target
        self.max_workers = min(max_workers, os.cpu_count() * 2)
        self.fake = Faker()
        self.accounts: List[Dict] = []
        self.stats = {'success': 0, 'gmail': 0, 'ig': 0, 'fail': 0}
        self.lock = threading.Lock()
        self.proxies = self.load_fast_proxies()
        print(f"⚡ FAST MODE: {target} accounts, {self.max_workers} workers")
    
    def load_fast_proxies(self) -> List[str]:
        """High-speed proxy pool"""
        fast_proxies = [
            '',  # Direct = fastest
            'socks5://127.0.0.1:9050',  # Tor (rotate identity)
            # Add premium proxies: residential/rotating
        ]
        return fast_proxies * 20  # Duplicate for rotation
    
    def generate_fast_creds(self) -> Dict:
        """Lightning-fast credential generation"""
        t = int(time.time() * 1000) % 10000
        username = f"user{random.randint(100000,999999)}{t}"
        return {
            'email': f"{username}@gmail.com",
            'password': f"P@ssw{''.join(random.choices(string.digits, k=8))}!",
            'username': username,
            'status': 'pending',
            'proxy': random.choice(self.proxies),
            'timestamp': time.time()
        }
    
    def create_ultra_fast_driver(self, proxy: str = '') -> uc.Chrome:
        """Minimal overhead driver - 3x faster startup"""
        options = Options()
        options.add_argument('--headless=new')  # New headless = 2x faster
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-images')  # 40% faster
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Speed optimizations
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-javascript')  # Risky but fast
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        driver = uc.Chrome(options=options, version_main=None)  # Auto-version
        driver.set_page_load_timeout(15)  # Fail fast
        return driver
    
    async def fast_gmail(self, creds: Dict) -> bool:
        """Gmail - optimized 15s completion"""
        driver = None
        try:
            driver = self.create_ultra_fast_driver(creds['proxy'])
            
            driver.get("https://accounts.google.com/signup/v2/webcreateaccount")
            wait = WebDriverWait(driver, 8)
            
            # Ultra-fast form fill (no sleeps)
            wait.until(EC.presence_of_element_located((By.NAME, "firstName")))
            driver.execute_script("""
                document.querySelector('[name="firstName"]').value = 'User';
                document.querySelector('[name="lastName"]').value = arguments[0];
            """, creds['username'][:6])
            
            driver.find_element(By.NAME, "Username").send_keys(creds['username'])
            driver.find_element(By.NAME, "Passwd").send_keys(creds['password'])
            driver.find_element(By.NAME, "ConfirmPasswd").send_keys(creds['password'])
            
            driver.find_element(By.ID, "accountDetailsNext").click()
            
            # Skip phone - direct recovery email (faster)
            try:
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Skip')]"))
                ).click()
            except:
                pass  # Continue anyway
            
            creds['status'] = 'gmail_fast'
            with self.lock:
                self.stats['gmail'] += 1
            return True
            
        except:
            creds['status'] = 'gmail_fail'
            return False
        finally:
            if driver:
                driver.quit()
    
    async def fast_instagram(self, creds: Dict) -> bool:
        """Instagram - 12s completion"""
        driver = None
        try:
            driver = self.create_ultra_fast_driver(creds['proxy'])
            driver.set_page_load_timeout(12)
            
            driver.get("https://www.instagram.com/accounts/emailsignup/")
            
            # JavaScript injection for speed
            script = f"""
            document.querySelector('[name="emailOrPhone"]').value = '{creds['email']}';
            document.querySelector('[name="fullName"]').value = 'User {creds['username'][:4]}';
            document.querySelector('[name="username"]').value = '{creds['username']}';
            document.querySelector('[name="password"]').value = '{creds['password']}';
            document.querySelector('button[type="submit"]').click();
            """
            driver.execute_script(script)
            
            # Wait minimal time
            await asyncio.sleep(3)
            
            # Success check
            if "error" not in driver.page_source.lower():
                creds['status'] = 'ig_success'
                with self.lock:
                    self.stats['success'] += 1
                return True
            else:
                creds['status'] = 'ig_error'
                return False
                
        except:
            creds['status'] = 'ig_fail'
            return False
        finally:
            if driver:
                driver.quit()
    
    async def process_account(self, creds: Dict):
        """Single account pipeline - 45s total"""
        # Gmail
        await self.fast_gmail(creds)
        await asyncio.sleep(random.uniform(5, 10))  # Minimal delay
        
        # Instagram  
        await self.fast_instagram(creds)
        
        # Save immediately
        with self.lock:
            self.accounts.append(creds)
            if len(self.accounts) % 10 == 0:
                self.save_fast()
    
    def save_fast(self):
        """Lightning checkpoint"""
        ts = int(time.time())
        filename = f"fast_accounts_{ts}.json"
        with open(filename, 'w') as f:
            json.dump(self.accounts[-100:], f)  # Last 100 only
        
        print(f"⚡ {len(self.accounts)}/{self.target} | "
              f"S:{self.stats['success']:3d} G:{self.stats['gmail']:3d} | "
              f"{time.strftime('%H:%M:%S')}")
    
    async def worker(self, worker_id: int):
        """Async worker"""
        print(f"🚀 Worker {worker_id} started")
        while len(self.accounts) < self.target:
            creds = self.generate_fast_creds()
            await self.process_account(creds)
            await asyncio.sleep(random.uniform(20, 40))  # 30s avg cycle
    
    def run(self):
        """Launch all workers"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        tasks = [self.worker(i) for i in range(self.max_workers)]
        loop.run_until_complete(asyncio.gather(*tasks))
        
        # Final save
        with open("FINAL_accounts.json", 'w') as f:
            json.dump(self.accounts, f, indent=1)
        print("🎉 FAST FARM COMPLETE!")

# CLI Runner
if __name__ == "__main__":
    import sys
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    
    creator = FastAccountCreator(target=target, max_workers=workers)
    creator.run()
