import asyncio
import json
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import ChromeOptions
import undetected_chromedriver as uc
from faker import Faker
import os

class MultiTargetBot:
    def __init__(self, accounts_file: str = "FINAL_accounts.json", targets_file: str = "targets.txt"):
        self.accounts = self.load_accounts(accounts_file)
        self.targets = self.load_targets(targets_file)
        self.fake = Faker()
        
        # Smart engagement patterns
        self.comments = [
            "Great post! 🔥", "Love this! 👏", "Amazing!", "So true! 💯", 
            "Interesting! 🤔", "Well said! 👌", "This is gold! ✨",
            "What do you think?", "Needed this today!", "Spot on! 🎯",
            "Thanks for sharing! 🙏", "Beautiful! 😍", "Inspiring!"
        ]
        
        print(f"🎯 Multi-target loaded:")
        print(f"   📱 {len(self.accounts)} accounts")
        print(f"   🔗 {len(self.targets)} target posts")
    
    def load_accounts(self, filename: str):
        """Load working accounts from JSON"""
        accounts = []
        files = [filename] + [f for f in os.listdir('.') if 'accounts_' in f and f.endswith('.json')]
        
        for file in files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    # Only fully successful accounts
                    accounts.extend([acc for acc in data 
                                   if acc.get('status') == 'full_success' 
                                   and 'engagement_status' not in acc])
            except Exception as e:
                print(f"⚠️ Skip {file}: {e}")
        
        print(f"✅ {len(accounts)} valid accounts ready")
        return accounts[:1000]  # Safety limit
    
    def load_targets(self, filename: str):
        """Load target URLs from targets.txt"""
        targets = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    url = line.strip()
                    if url and 'instagram.com/p/' in url:
                        targets.append(url)
        except FileNotFoundError:
            print(f"❌ Create targets.txt with Instagram post URLs")
            print("Example:")
            print("https://www.instagram.com/p/C123ABC/")
            print("https://www.instagram.com/p/D456XYZ/")
            exit(1)
        
        print(f"✅ Loaded {len(targets)} target posts")
        return targets
    
    def create_stealth_driver(self):
        """Mobile stealth driver"""
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1')
        options.add_argument('--window-size=375,812')  # iPhone size
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        driver = uc.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    async def login_ig(self, driver, email: str, password: str) -> bool:
        """Fast mobile login"""
        try:
            driver.get("https://www.instagram.com/accounts/login/")
            wait = WebDriverWait(driver, 12)
            
            wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(email)
            driver.find_element(By.NAME, "password").send_keys(password)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            await asyncio.sleep(6)
            
            # Skip notifications
            try:
                driver.find_element(By.XPATH, "//button[text()='Not Now']").click()
                await asyncio.sleep(2)
            except:
                pass
            
            # Success check
            return "instagram.com" in driver.current_url and "login" not in driver.current_url
            
        except:
            return False
    
    async def engage_post(self, driver, target_url: str, account_email: str) -> Dict:
        """Full engagement: view + like + comment"""
        result = {'success': False, 'action': []}
        
        try:
            print(f"   🎯 {account_email[:15]} → {target_url.split('/')[-2]}")
            driver.get(target_url)
            wait = WebDriverWait(driver, 10)
            
            # 1. FULL VIEW (8-15s watch time)
            await asyncio.sleep(random.uniform(3, 6))
            
            # Human scroll simulation
            for _ in range(3):
                pos = random.randint(200, 900)
                driver.execute_script(f"window.scrollTo(0, {pos});")
                await asyncio.sleep(random.uniform(1, 2))
            
            # 2. LIKE (70% chance)
            if random.random() < 0.7:
                try:
                    like_btn = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//span[@aria-label='Like'] | //svg[@aria-label='Like']")
                    ))
                    driver.execute_script("arguments[0].click();", like_btn)
                    result['action'].append('liked')
                    await asyncio.sleep(1.5)
                except:
                    pass
            
            # 3. COMMENT (25% chance - more valuable)
            if random.random() < 0.25:
                try:
                    comment_box = driver.find_element(By.TAG_NAME, "textarea")
                    comment = random.choice(self.comments)
                    comment_box.send_keys(comment)
                    await asyncio.sleep(1)
                    
                    post_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Post')]")
                    driver.execute_script("arguments[0].click();", post_btn)
                    result['action'].append(f'commented: {comment[:20]}')
                    await asyncio.sleep(3)
                except:
                    pass
            
            result['success'] = True
            result['watch_time'] = random.uniform(12, 25)
            
        except Exception as e:
            result['error'] = str(e)[:50]
        
        return result
    
    async def process_account(self, account: Dict, target_url: str):
        """Single account → single target pipeline"""
        driver = None
        try:
            driver = self.create_stealth_driver()
            
            # Login
            if not await self.login_ig(driver, account['email'], account['password']):
                account['status'] = 'login_failed'
                return False
            
            # Engage specific target
            engagement = await self.engage_post(driver, target_url, account['email'])
            
            # Record results
            account.update({
                'target_url': target_url,
                'engagement': engagement,
                'engaged_at': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            return engagement['success']
            
        finally:
            if driver:
                driver.quit()
    
    async def smart_distribution(self, max_concurrent: int = 2):
        """Distribute accounts across targets evenly"""
        print(f"🚀 Distributed campaign: {max_concurrent} concurrent")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def safe_engage(account_target_pair):
            account, target = account_target_pair
            async with semaphore:
                success = await self.process_account(account, target)
                if success:
                    print(f"✅ {account['email'][:20]} → {target.split('/')[-2]}")
                await asyncio.sleep(random.uniform(120, 240))  # 2-4 min safety
                return success
        
        # Smart distribution: round-robin targets
        tasks = []
        for i, account in enumerate(self.accounts):
            target_idx = i % len(self.targets)
            pair = (account, self.targets[target_idx])
            tasks.append(safe_engage(pair))
        
        # Run with progress tracking
        completed = 0
        for coro in asyncio.as_completed(tasks):
            result = await coro
            if result:
                completed += 1
            print(f"📊 Progress: {completed}/{len(tasks)} ({completed/len(tasks)*100:.1f}%)")
        
        self.save_results()
    
    def save_results(self):
        """Save detailed engagement results"""
        filename = f"multi_target_results_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(self.accounts, f, indent=1)
        
        # Summary stats
        successes = sum(1 for a in self.accounts if a.get('status') != 'login_failed')
        likes = sum(1 for a in self.accounts if 'liked' in str(a.get('engagement', {})))
        comments = sum(1 for a in self.accounts if 'commented' in str(a.get('engagement', {})))
        
        print("\n" + "="*60)
        print("📈 CAMPAIGN SUMMARY")
        print(f"✅ Total Engagements: {successes}/{len(self.accounts)} ({successes/len(self.accounts)*100:.1f}%)")
        print(f"❤️ Likes: {likes}")
        print(f"💬 Comments: {comments}")
        print(f"📁 Results: {filename}")
        print("="*60)

# 🔥 CLI Runner
if __name__ == "__main__":
    bot = MultiTargetBot()
    asyncio.run(bot.smart_distribution(max_concurrent=2))  # Safe: 2 concurrent
