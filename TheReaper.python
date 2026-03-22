import asyncio
import json
import time
import random
import os
import aiohttp
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from faker import Faker
import threading
from typing import List, Dict
from PIL import Image
import io

class GlobalPfpCreator:
    def __init__(self, target: int = 50, max_workers: int = 2):
        self.target = target
        self.max_workers = min(max_workers, os.cpu_count())
        
        # Create organized folders
        os.makedirs("accounts", exist_ok=True)
        os.makedirs("accounts/pfps", exist_ok=True)
        os.makedirs("accounts/pfps/shona", exist_ok=True)
        os.makedirs("accounts/pfps/anime", exist_ok=True)
        os.makedirs("accounts/pfps/nature", exist_ok=True)
        os.makedirs("accounts/pfps/pets", exist_ok=True)
        os.makedirs("accounts/pfps/cars", exist_ok=True)
        
        self.gmail_accounts: List[Dict] = []
        self.ig_accounts: List[Dict] = []
        self.full_accounts: List[Dict] = []
        self.stats = {'gmail': 0, 'ig': 0, 'full': 0, 'pfp': 0}
        self.lock = threading.Lock()
        
        # Profile picture categories (NO human faces)
        self.pfp_categories = {
            'shona': 'accounts/pfps/shona',
            'anime': 'accounts/pfps/anime', 
            'nature': 'accounts/pfps/nature',  # flowers/birds
            'pets': 'accounts/pfps/pets',
            'cars': 'accounts/pfps/cars'
        }
        
        # Pre-populate with direct URLs (fast, reliable)
        self.pfp_urls = {
            'shona': [
                "https://i.imgur.com/pattern1.jpg",  # African patterns
                "https://i.imgur.com/shona_art.png",  # Shona art
                # Add your hosted images or use bulk download below
            ],
            'anime': [
                "https://i.imgur.com/anime_avat1.png",
                "https://i.imgur.com/anime_avat2.png",
                # Cute anime avatars
            ],
            'nature': [
                "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=300",  # Flowers
                "https://images.unsplash.com/photo-1570549717069-33bed2ebafec?w=300",  # Birds
            ],
            'pets': [
                "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=300",  # Cats
                "https://images.unsplash.com/photo-1561948955-570b270e7c36?w=300",  # Dogs
            ],
            'cars': [
                "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=300",  # Sports cars (no plates)
                "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=300",
            ]
        }
        
        # Global names (same as before)
        self.global_cultures = {
            'shona': {'male': ['Tino', 'Tinashe'], 'female': ['Shamie', 'Tamie'], 'last': ['Magumbo', 'Mafara']},
            'english': {'male': ['James', 'Oliver'], 'female': ['Olivia', 'Emma'], 'last': ['Smith', 'Taylor']},
            'japanese': {'male': ['Hiroto', 'Yuto'], 'female': ['Hinata', 'Yui'], 'last': ['Sato', 'Suzuki']},
            # ... (full list from previous)
        }
        
        print(f"🎨 GLOBAL + PFPS: {target} accounts with cartoon/anime/nature pics")
    
    async def download_pfp(self, session: aiohttp.ClientSession, category: str, profile_id: str) -> str:
        """Download and save profile picture"""
        try:
            folder = self.pfp_categories[category]
            filename = f"{profile_id}.jpg"
            filepath = os.path.join(folder, filename)
            
            if os.path.exists(filepath):
                return filepath
            
            # Pick random URL
            url = random.choice(self.pfp_urls.get(category, self.pfp_urls['nature']))
            
            async with session.get(url) as resp:
                if resp.status == 200:
                    img_data = await resp.read()
                    img = Image.open(io.BytesIO(img_data))
                    img = img.resize((300, 300))  # IG standard
                    img.save(filepath, 'JPEG', quality=85)
                    
                    with self.lock:
                        self.stats['pfp'] += 1
                    
                    return filepath
            
        except:
            pass
        
        # Fallback generic
        return self.create_generic_pfp(profile_id)
    
    def create_generic_pfp(self, profile_id: str) -> str:
        """Create colorful gradient fallback"""
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (300, 300), color=(random.randint(100,255), random.randint(100,255), random.randint(100,255)))
        draw = ImageDraw.Draw(img)
        draw.text((100, 130), profile_id[:2].upper(), fill=(255,255,255), font_size=40)
        filepath = f"accounts/pfps/generic/{profile_id}.jpg"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        img.save(filepath)
        return filepath
    
    def generate_global_profile(self) -> Dict:
        """Profile with PFP category"""
        culture = random.choice(list(self.global_cultures.keys()))
        gender = random.choice(['male', 'female'])
        
        names = self.global_cultures[culture]
        profile = {
            'culture': culture,
            'gender': gender,
            'first_name': random.choice(names[gender]),
            'last_name': random.choice(names['last']),
            'username': f"smilie{random.randint(100,999)}{random.choice(['😘','🥰','✨'])}",
            'email': f"smilie{random.randint(100,999)}@gmail.com",
            'password': f"{random.choice(names[gender])[0].upper()}123!zW",
            'pfp_category': random.choice(['anime', 'nature', 'pets', 'cars', 'shona']),
        }
        profile['full_name'] = f"{profile['first_name']} {profile['last_name']}"
        return profile
    
    async def create_gmail_with_pfp(self, profile: Dict, http_session: aiohttp.ClientSession):
        """Gmail + download PFP"""
        # Download PFP first
        profile['profile_picture'] = await self.download_pfp(http_session, profile['pfp_category'], profile['profile_id'])
        
        # Gmail creation (same logic as before)
        driver = self.create_stealth_driver()
        try:
            # ... Gmail form filling ...
            profile['gmail_status'] = 'created'
            self.gmail_accounts.append(profile.copy())
            self.stats['gmail'] += 1
            self.save_gmail()
        finally:
            driver.quit()
    
    # ... (rest of Gmail/IG methods same as previous)
    
    def save_gmail(self):
        with open("accounts/g_accounts.json", 'w') as f:
            json.dump(self.gmail_accounts, f, indent=2)
    
    def save_ig(self):
        with open("accounts/ig_accounts.json", 'w') as f:
            json.dump(self.ig_accounts, f, indent=2)
    
    def save_full(self):
        with open("accounts/full_accounts.json", 'w') as f:
            json.dump(self.full_accounts, f, indent=2)

# Quick PFP Bulk Downloader
async def bulk_download_pfps():
    """One-time PFP downloader"""
    urls = {
        'anime': ['https://example.com/anime1.jpg', 'https://example.com/anime2.png'],
        'nature': ['https://unsplash.com/flowers1.jpg'],
        # Add 100+ URLs
    }
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for category, url_list in urls.items():
            for i, url in enumerate(url_list):
                tasks.append(download_single_pfp(session, category, f"{i:03d}", url))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    creator = GlobalPfpCreator(50)
    creator.run()
