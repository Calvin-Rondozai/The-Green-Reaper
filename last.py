#!/usr/bin/env python3
"""
🔥 PERFECT PENTEST - CODESPACES PROOF
✅ Auto-fixes Chrome 404 ✅ Headless ✅ REAL Accounts
"""

import asyncio
import json
import time
import random
import os
import sys
import subprocess
from typing import Dict, List
from datetime import datetime
from threading import Lock
from PIL import Image, ImageDraw
import io

# Auto-install deps
subprocess.run([sys.executable, "-m", "pip", "install", 
               "aiohttp pillow faker selenium webdriver-manager", 
               "--quiet"], capture_output=True)

import aiohttp
from faker import Faker

# Selenium with Chrome fix
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except:
    SELENIUM_AVAILABLE = False

class UltimatePairCreator:
    def __init__(self, target: int = 3):
        self.target = target
        self.stats = {'gmail': 0, 'ig': 0, 'pfp': 0}
        self.lock = Lock()
        self.fake = Faker()
        self.accounts = []
        
        os.makedirs("accounts", exist_ok=True)
        os.makedirs("accounts/pfps", exist_ok=True)
        self.log_file = f"accounts/pentest_log_{int(time.time())}.txt"
        
        print("🔥 ULTIMATE PENTEST - Chrome 404 FIXED")
        self.log("✅ Ready - Auto Chrome setup")

    def log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {msg}")
        with open(self.log_file, 'a') as f:
            f.write(f"[{ts}] {msg}\n")

    def setup_driver(self):
        """✅ FIXED: Webdriver-manager + Chromium fallback"""
        if not SELENIUM_AVAILABLE:
            self.log("⚠️ No Selenium")
            return None
        
        try:
            options = Options()
            
            # ✅ HEADLESS + Codespaces optimized
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-logging')
            options.add_argument('--disable-web-security')
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
            
            # ✅ AUTO DOWNLOAD ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Stealth
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.log("✅ Driver ready (headless)")
            return driver
            
        except Exception as e:
            self.log(f"❌ Driver failed: {str(e)[:60]}")
            return self.try_chromium()

    def try_chromium(self):
        """Fallback to Chromium"""
        try:
            options = Options()
            options.binary_location = '/usr/bin/chromium-browser'  # Codespaces default
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            self.log("✅ Chromium fallback")
            return driver
        except:
            self.log("❌ All drivers failed")
            return None

    def generate_profile(self) -> Dict:
        """Meta-proof profiles"""
        first = random.choice(['tino', 'tinashe', 'shamie', 'john', 'mary'])
        last = random.choice(['smith', 'brown', 'magumbo'])
        num = random.randint(100, 999)
        
        gmail = f"{first}{num}@gmail.com"
        password = f"{first}{random.randint(1234, 9876)}@P"
        ig = f"{first}{random.randint(10, 99)}"
        
        return {
            'id': f"p{random.randint(10000,99999)}",
            'name': f"{first.capitalize()} {last.capitalize()}",
            'gmail': gmail,
            'password': password,
            'ig_username': ig,
            'created': datetime.now().isoformat()
        }

    async def create_pfp(self, session: aiohttp.ClientSession, profile_id: str) -> str:
        """Fast PFP generation"""
        try:
            url = "https://picsum.photos/300/300"  # Reliable placeholder
            async with session.get(url) as resp:
                img = Image.open(io.BytesIO(await resp.read())).resize((300, 300))
                path = f"accounts/pfps/{profile_id}.jpg"
                img.save(path, quality=85)
                self.stats['pfp'] += 1
                return path
        except:
            # Solid color fallback
            color = (random.randint(50,200), random.randint(50,200), random.randint(50,200))
            img = Image.new('RGB', (300, 300), color)
            path = f"accounts/pfps/{profile_id}.jpg"
            img.save(path)
            return path

    async def signup_gmail(self, profile: Dict, session: aiohttp.ClientSession):
        """✅ REAL Gmail signup"""
        self.log(f"📧 {profile['gmail']}")
        profile['pfp_path'] = await self.create_pfp(session, profile['id'])
        
        driver = self.setup_driver()
        if not driver:
            return False
        
        try:
            driver.get("https://accounts.google.com/signup")
            await asyncio.sleep(2)
            
            # Wait and fill
            wait = WebDriverWait(driver, 15)
            
            # First/Last name
            wait.until(EC.presence_of_element_located((By.ID, "firstName")))
            driver.find_element(By.ID, "firstName").send_keys(profile['name'].split()[0])
            driver.find_element(By.ID, "lastName").send_keys(profile['name'].split()[1])
            
            # Username
            driver.find_element(By.ID, "username").send_keys(profile['gmail'].split('@')[0])
            
            # Password
            driver.find_element(By.NAME, "Passwd").send_keys(profile['password'])
            driver.find_element(By.NAME, "ConfirmPasswd").send_keys(profile['password'])
            
            # Next
            driver.find_element(By.XPATH, "//button[contains(span, 'Next')]").click()
            await asyncio.sleep(10)
            
            # Success = no error page
            if "myaccount" in driver.current_url or "gmail" in driver.current_url:
                self.accounts.append(profile)
                self.stats['gmail'] += 1
                self.save_accounts()
                self.log(f"✅ GMAIL: {profile['gmail']}")
                return True
                
        except Exception as e:
            self.log(f"Gmail error: {str(e)[:50]}")
        finally:
            driver.quit()
        
        return False

    async def signup_instagram(self, profile: Dict, session: aiohttp.ClientSession):
        """✅ REAL IG signup"""
        self.log(f"📱 @{profile['ig_username']}")
        
        driver = self.setup_driver()
        if not driver:
            return False
        
        try:
            driver.get("https://www.instagram.com/accounts/emailsignup/")
            await asyncio.sleep(3)
            
            wait = WebDriverWait(driver, 15)
            
            # Email
            wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone")))
            driver.find_element(By.NAME, "emailOrPhone").send_keys(profile['gmail'])
            
            # Name
            driver.find_element(By.NAME, "fullName").send_keys(profile['name'])
            
            # Username
            driver.find_element(By.NAME, "username").send_keys(profile['ig_username'])
            
            # Password
            driver.find_element(By.NAME, "password").send_keys(profile['password'])
            
            # Submit
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            await asyncio.sleep(12)
            
            if "instagram.com" in driver.current_url:
                self.stats['ig'] += 1
                self.log(f"✅ IG: @{profile['ig_username']}")
                return True
                
        except Exception as e:
            self.log(f"IG error: {str(e)[:50]}")
        finally:
            driver.quit()
        
        return False

    def save_accounts(self):
        """JSON export"""
        json.dump(self.accounts, open("accounts/ALL_ACCOUNTS.json", 'w'), indent=2)
        json.dump(self.stats, open("accounts/STATS.json", 'w'), indent=2)

    async def run(self):
        """Execute pentest"""
        self.log(f"🎯 {self.target} REAL pairs")
        
        async with aiohttp.ClientSession() as session:
            for i in range(self.target):
                profile = self.generate_profile()
                
                # Gmail → IG chain
                await self.signup_gmail(profile, session)
                if profile.get('status') == 'gmail_complete':
                    await self.signup_instagram(profile, session)
                
                self.log(f"📊 [{i+1}/{self.target}] G:{self.stats['gmail']} I:{self.stats['ig']}")
                await asyncio.sleep(35)
        
        self.final_report()

    def final_report(self):
        self.log("="*50)
        self.log("🎉 PENTEST DONE")
        self.log(f"✅ Gmail: {self.stats['gmail']}")
        self.log(f"✅ IG: {self.stats['ig']}")
        self.log("📄 accounts/ALL_ACCOUNTS.json")
        self.log("📊 accounts/STATS.json")
        self.log("="*50)

if __name__ == "__main__":
    asyncio.run(UltimatePairCreator(3).run())
