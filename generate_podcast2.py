import requests
import xml.etree.ElementTree as ET
import edge_tts
import asyncio
import datetime
import os
import glob

# --- CONFIGURATION ---
RSS_URL = "https://thehackernews.com/feeds/posts/default?alt=rss"
OUTPUT_DIR = "."
RETENTION_DAYS = 7

def get_today_date():
    return datetime.date.today().strftime("%Y-%m-%d")

def fetch_news():
    """Fetch top 3 headlines from The Hacker News RSS"""
    try:
        response = requests.get(RSS_URL, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        items = []
        # Get first 3 items from RSS
        for item in root.findall('.//item')[:3]:
            title = item.find('title').text
            link = item.find('link').text
            items.append((title, link))
        return items
    except Exception as e:
        print(f"Error fetching news: {e}")
        return [("無法連接新聞源", "")]

def generate_script(news_items):
    """Generate Cantonese podcast script"""
    today = get_today_date()
    script = f"""大家早晨！歡迎收聽《IT Cybersecurity 日報》！今日係 {today}。
我哋今集為大家總結咗 {len(news_items)} 條最重要嘅網絡安全新聞。

"""
    for i, (title, link) in enumerate(news_items, 1):
        script += f"第{i}條新聞：{title}。\n"
        script += f"詳情可以參考來源：{link}\n\n"
    
    script += "多謝大家收聽《IT Cybersecurity 日報》，記住保持警覺，保護好自己嘅數字資產。我哋明日再見！"
    return script

async def create_mp3(text, filename):
    """Generate MP3 using Edge TTS"""
    communicate = edge_tts.Communicate(
        text, 
        "zh-HK-HiuMaanNeural", 
        rate="+10%"
    )
    await communicate.save(filename)
    print(f"✅ MP3 generated: {filename}")

def cleanup_old_files():
    """Delete MP3 files older than 7 days"""
    cutoff = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)
    for f in glob.glob(os.path.join(OUTPUT_DIR, "*_IT_Cybersecurity*.mp3")):
        if datetime.datetime.fromtimestamp(os.path.getmtime(f)) < cutoff:
            os.remove(f)
            print(f"🗑️ Deleted old file: {f}")

async def main():
    print("🚀 Starting Daily Podcast Generation...")
    
    # 1. Fetch News
    news = fetch_news()
    
    # 2. Generate Script
    script_text = generate_script(news)
    
    # Save script to file (for website display)
    script_filename = f"{get_today_date()}_script.txt"
    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(script_text)
    print(f"📝 Script saved: {script_filename}")
    
    # 3. Generate Audio
    mp3_filename = f"{get_today_date()}_IT_Cybersecurity.mp3"
    await create_mp3(script_text, mp3_filename)
    
    # 4. Cleanup Old Files
    cleanup_old_files()
    
    print("✨ All done!")


import json

def update_manifest(current_episode):
    """Update or create manifest.json for the website"""
    manifest_file = "manifest.json"
    episodes = []
    
    # Load existing manifest if it exists
    if os.path.exists(manifest_file):
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                episodes = json.load(f)
        except:
            episodes = []
    
    # Add new episode (avoid duplicates)
    if not any(e['date'] == current_episode['date'] for e in episodes):
        episodes.append(current_episode)
    
    # Keep only last 7 entries in manifest too
    episodes = episodes[-7:]
    
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(episodes, f, ensure_ascii=False, indent=2)
    print(f"📋 Manifest updated with {len(episodes)} episodes")

# ... inside main() function, after creating MP3 ...
    # Add this before cleanup_old_files()
    current_ep = {
        "date": get_today_date(),
        "mp3": mp3_filename,
        "script": script_text.replace("\n", "<br>"),
        "sources": [{"title": t, "url": l} for t, l in news]
    }
    update_manifest(current_ep)

# Add this function to the bottom of your generate_podcast.py (before if __name__ == "__main__":) and call it in main():

if __name__ == "__main__":
    asyncio.run(main())