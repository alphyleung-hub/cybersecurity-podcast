import feedparser
import edge_tts
import asyncio
import datetime
import os
import glob
import json

# --- 配置 ---
RSS_URL = "https://thehackernews.com/feeds/posts/default?alt=rss"
RETENTION_DAYS = 7

def get_today_date():
    return datetime.date.today().strftime("%Y年%m月%d日")

def fetch_real_news():
    """實時從 The Hacker News 抓取最新 3 條新聞。如果失敗則直接報錯，絕不使用假數據。"""
    print(f"📡 正在實時連接 The Hacker News RSS: {RSS_URL}")
    try:
        feed = feedparser.parse(RSS_URL)
        
        # 檢查是否成功解析
        if feed.bozo:
            raise Exception(f"RSS 解析失敗: {feed.bozo_exception}")
            
        if not feed.entries:
            raise Exception("RSS 返回空數據，沒有找到任何新聞。")
            
        news_items = []
        # 只取最新 3 條
        for entry in feed.entries[:3]:
            news_items.append({
                "title": entry.title,
                "link": entry.link
            })
            print(f"  ✅ 成功抓取: {entry.title}")
            
        return news_items
        
    except Exception as e:
        print(f"❌ 致命錯誤：無法抓取真實新聞！")
        print(f"錯誤詳情: {e}")
        print("⚠️ 腳本將停止運行，絕不生成硬編碼的假新聞。")
        raise # 直接拋出異常，讓 GitHub Actions 顯示紅字失敗

def generate_dynamic_script(news_items):
    """將真實抓取到的新聞標題，動態嵌入到廣東話對話模板中"""
    today = get_today_date()
    
    # 提取真實標題和連結
    n1_title = news_items[0]["title"]
    n1_link = news_items[0]["link"]
    n2_title = news_items[1]["title"] if len(news_items) > 1 else "其他網絡安全動態"
    n2_link = news_items[1]["link"] if len(news_items) > 1 else "https://thehackernews.com/"
    n3_title = news_items[2]["title"] if len(news_items) > 2 else "行業安全提示"
    n3_link = news_items[2]["link"] if len(news_items) > 2 else "https://thehackernews.com/"

    # 動態對話腳本模板 (將真實英文標題融入廣東話對話)
    script = f"""[阿希][female][warm and enthusiastic, friendly news anchor tone]:
大家早晨！歡迎收聽《IT Cybersecurity 日報》！今日係 {today}。我哋今集為大家總結咗 3 條 IT cybersecurity 界嘅重要新聞。今日嘅內容真係有啲震撼，由最新嘅漏洞報導，到企業系統安全，全部都成為黑客嘅目標。無論你係 IT 新手、在職人士，定係想追新聞但冇時間睇文章嘅普通人，今集都啱晒你。準備好未？我哋即刻開始啦！

[阿明][male][curious and easy-going]:
早晨，阿希！聽你咁講，今日嘅新聞好似同我哋日常生活好有關係喎。我已經準備好筆記簿，等我哋即刻進入第一條新聞啦。

[阿希][female][warm and enthusiastic, friendly news anchor tone]:
無錯，第一條新聞，係今日嘅頭條。根據 The Hacker News 最新報導：{n1_title}。

[阿明][male][curious and easy-going]:
哇，{n1_title}？聽落去好專業。阿希，可唔可以用簡單嘅廣東話，解釋下呢單新聞同我哋普通人有咩關係？

[阿希][female][warm and enthusiastic, friendly news anchor tone]:
無問題！簡單嚟講，呢類新聞通常代表黑客發現咗一個新嘅安全漏洞，或者發起咗新嘅攻擊活動。雖然標題係英文，但核心意思係：我哋日常使用嘅軟件或系統，可能存在未被修復嘅風險。如果黑客成功利用，佢哋可能會竊取個人資料或破壞系統運作。

[阿明][male][curious and easy-going]:
嘩，咁即係話，如果我哋唔理會呢啲警告，隨時會中招？咁我哋應該點樣保護自己？

[阿希][female][warm and enthusiastic, friendly news anchor tone]:
最簡單有效嘅方法有兩個：第一，即刻檢查並更新你手機同電腦上嘅所有應用軟件；第二，唔好點擊來路不明嘅電郵連結或附件。對於想深入了解嘅聽眾，可以前往 {n1_link} 查看完整英文報導。

[阿明][male][curious and easy-going]:
收到！更新軟件同保持警覺，永遠係第一道防線。咁我哋睇下第二條新聞，聽講都係最新嘅安全動態？

[阿希][female][warm and enthusiastic, friendly news anchor tone]:
係嘅，第二條新聞同樣來自 The Hacker News：{n2_title}。

[阿明][male][curious and easy-going]:
呢個標題又係滿滿嘅技術術語。對於唔係做 IT 嘅普通人，我哋需要擔心咩？

[阿希][female][warm and enthusiastic, friendly news anchor tone]:
其實唔使過度恐慌，但要保持關注。呢類報導通常係安全研究員發現咗潛在威脅，並已經通知相關公司修復。佢提醒我哋，網絡世界嘅威脅係不斷進化嘅。企業需要加強防禦，而我哋作為用戶，就要養成良好嘅密碼管理習慣，例如啟用雙重認證 (2FA)。

[阿明][male][curious and easy-going]:
明白晒。原來安全研究員就好似網絡世界嘅「免疫系統」，幫我先發現病毒。咁最後一條新聞呢？

[阿希][female][warm and enthusiastic, friendly news anchor tone]:
最後一條新聞係：{n3_title}。詳細資訊可以參考 {n3_link}。

[阿明][male][curious and easy-going]:
聽完今日嘅三條真實新聞，真係覺得 cybersecurity 無處不在。由頭條漏洞，到行業動態，每一步都唔可以馬虎。

[阿希][female][warm and enthusiastic, friendly news anchor tone]:
無錯，阿明總結得好好。今日嘅新聞反映出一個明顯嘅趨勢：黑客嘅攻擊面正不斷擴大。這提醒我哋，網絡安全唔單止係 IT 部門嘅責任，而係每個數字公民嘅必修課。

[阿希][female][warm and enthusiastic, friendly news anchor tone]:
今日嘅新聞全部實時抓取自 The Hacker News (https://thehackernews.com/)。多謝大家收聽今集嘅《IT Cybersecurity 日報》。記住，保持警覺，及時更新，守護好自己嘅數字生活。我哋下集再見！
"""
    return script

async def create_mp3(text, filename):
    """生成 MP3"""
    print(f"🎙️ 正在生成語音 (這可能需要 1-2 分鐘): {filename} ...")
    try:
        communicate = edge_tts.Communicate(text, "zh-HK-HiuMaanNeural", rate="+10%")
        await communicate.save(filename)
        print(f"✅ MP3 生成成功！")
    except Exception as e:
        print(f"❌ MP3 生成失敗: {e}")
        raise

def cleanup_old_files():
    """刪除 7 天前的舊 MP3"""
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
    """更新網站用的 manifest.json"""
    manifest_file = "manifest.json"
    episodes = []
    if os.path.exists(manifest_file):
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                episodes = json.load(f)
        except:
            episodes = []
    
    episodes = [e for e in episodes if e['date'] != current_episode['date']]
    episodes.append(current_episode)
    episodes = episodes[-7:]
    
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(episodes, f, ensure_ascii=False, indent=2)
    print(f"📋 Manifest 已更新，共 {len(episodes)} 集")

async def main():
    print("🚀 開始每日播客生成流程 (純動態抓取模式)...")
    
    # 1. 實時抓取 (如果失敗會直接 raise Exception，絕不 hard code)
    news = fetch_real_news()
    
    # 2. 動態生成腳本
    script_text = generate_dynamic_script(news)
    
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    script_filename = f"{today_str}_script.txt"
    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(script_text)
    print(f"📝 腳本已儲存: {script_filename}")
    
    # 3. 生成 MP3
    mp3_filename = f"{today_str}_IT_Cybersecurity.mp3"
    await create_mp3(script_text, mp3_filename)
    
    # 4. 更新 Manifest
    current_ep = {
        "date": today_str,
        "mp3": mp3_filename,
        "script": script_text.replace("\n", "<br>"),
        "sources": [{"title": n["title"], "url": n["link"]} for n in news]
    }
    update_manifest(current_ep)
    
    # 5. 清理
    cleanup_old_files()
    
    print("✨ 全部完成！")

if __name__ == "__main__":
    asyncio.run(main())