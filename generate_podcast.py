import requests
import xml.etree.ElementTree as ET
import edge_tts
import asyncio
import datetime
import os
import glob
import json

# --- 配置 ---
RSS_URL = "https://thehackernews.com/feeds/posts/default?alt=rss"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'} # 防止被網站封鎖
RETENTION_DAYS = 7

def get_today_date():
    return datetime.date.today().strftime("%Y-%m-%d")

def fetch_news():
    """抓取新聞，加入錯誤保護"""
    print("📡 正在嘗試連接 The Hacker News...")
    try:
        response = requests.get(RSS_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        items = []
        for item in root.findall('.//item')[:3]: # 只取前 3 條
            title = item.find('title').text
            link = item.find('link').text
            items.append((title, link))
            print(f"  ✅ 找到新聞: {title}")
            
        if not items:
            raise Exception("RSS 返回空數據")
        return items
        
    except Exception as e:
        print(f"❌ 抓取新聞失敗: {e}")
        print("⚠️ 使用備用新聞數據...")
        # 備用數據，防止腳本完全崩潰
        return [
            ("GitHub Actions 自動化測試成功", "https://github.com"),
            ("Edge TTS 語音合成正常", "https://azure.microsoft.com"),
            ("Cloudflare Pages 部署完成", "https://cloudflare.com")
        ]

def generate_script(news_items):
    today = get_today_date()
    script = f"大家早晨！歡迎收聽《IT Cybersecurity 日報》！今日係 {today}。\n\n"
    
    for i, (title, link) in enumerate(news_items, 1):
        script += f"第{i}條新聞：{title}。\n"
        script += f"詳情來源：{link}\n\n"
        
    script += "多謝大家收聽，記住保持警覺，保護好自己嘅數字資產。我哋明日再見！"
    return script

async def create_mp3(text, filename):
    print(f"🎙️ 正在生成語音: {filename} ...")
    try:
        communicate = edge_tts.Communicate(text, "zh-HK-HiuMaanNeural", rate="+10%")
        await communicate.save(filename)
        print(f"✅ MP3 生成成功！")
    except Exception as e:
        print(f"❌ MP3 生成失敗: {e}")
        raise # 讓 GitHub Actions 知道這步失敗了

def cleanup_old_files():
    print("🧹 清理舊文件...")
    cutoff = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)
    for f in glob.glob("*_IT_Cybersecurity*.mp3"):
        try:
            if datetime.datetime.fromtimestamp(os.path.getmtime(f)) < cutoff:
                os.remove(f)
                print(f"  🗑️ 已刪除: {f}")
        except Exception:
            pass

def update_manifest(current_episode):
    manifest_file = "manifest.json"
    episodes = []
    if os.path.exists(manifest_file):
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                episodes = json.load(f)
        except:
            episodes = []
    
    # 移除舊的同日期記錄
    episodes = [e for e in episodes if e['date'] != current_episode['date']]
    episodes.append(current_episode)
    episodes = episodes[-7:] # 只保留最近 7 天
    
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(episodes, f, ensure_ascii=False, indent=2)
    print(f"📋 Manifest 已更新")

async def main():
    print("🚀 開始每日播客生成流程...")
    
    # 1. 抓取
    news = fetch_news()
    
    # 2. 腳本
    script_text = generate_script(news)
    script_filename = f"{get_today_date()}_script.txt"
    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(script_text)
        
    # 3. 語音
    mp3_filename = f"{get_today_date()}_IT_Cybersecurity.mp3"
    await create_mp3(script_text, mp3_filename)
    
    # 4. 更新網站數據
    current_ep = {
        "date": get_today_date(),
        "mp3": mp3_filename,
        "script": script_text.replace("\n", "<br>"),
        "sources": [{"title": t, "url": l} for t, l in news]
    }
    update_manifest(current_ep)
    
    # 5. 清理
    cleanup_old_files()
    print("✨ 全部完成！")

if __name__ == "__main__":
    asyncio.run(main())