import discord
from discord.ext import commands, tasks
import os
import asyncio
from keep_alive import keep_alive

# 請將這裡替換成你要機器人掛機的「語音頻道 ID」
TARGET_VC_ID = 1449627369672540170

intents = discord.Intents.default()
# 如果你的機器人沒有要讀取訊息，只需要預設 intents 即可
bot = commands.Bot(command_prefix="!", intents=intents)

async def connect_to_vc():
    """負責連線到指定語音頻道的函式"""
    await bot.wait_until_ready()
    channel = bot.get_channel(TARGET_VC_ID)
    
    if not channel:
        print("❌ 找不到指定的語音頻道，請檢查 ID 是否正確！")
        return
    
    # 檢查是否已經在語音頻道內
    voice = discord.utils.get(bot.voice_clients, guild=channel.guild)
    if voice and voice.is_connected():
        return

    try:
        await channel.connect()
        print(f"✅ 成功加入語音頻道：{channel.name}")
    except Exception as e:
        print(f"⚠️ 連線失敗：{e}")

@bot.event
async def on_ready():
    print(f"🤖 登入成功：{bot.user}")

    # 🌟 在這裡加上設定機器人狀態的程式碼 🌟
    # ActivityType.playing = 正在玩
    # ActivityType.watching = 正在觀看
    # ActivityType.listening = 正在聆聽
    activity = discord.Activity(type=discord.ActivityType.watching, name="🌌 今晚的星空")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    # 啟動時馬上連線
    bot.loop.create_task(connect_to_vc())
    # 啟動定時檢查任務
    if not check_connection.is_running():
        check_connection.start()

@tasks.loop(minutes=5)
async def check_connection():
    """每 5 分鐘主動檢查一次連線狀態，應對網路波動"""
    channel = bot.get_channel(TARGET_VC_ID)
    if channel:
        voice = discord.utils.get(bot.voice_clients, guild=channel.guild)
        if not voice or not voice.is_connected():
            print("🔄 偵測到斷線，正在嘗試重新連線...")
            await connect_to_vc()

@bot.event
async def on_voice_state_update(member, before, after):
    """監聽語音狀態：如果機器人被意外移出頻道，馬上重連"""
    # 確認是機器人自己，且從「有頻道」變成「無頻道 (斷線)」
    if member == bot.user and before.channel is not None and after.channel is None:
        print("⚡ 機器人被移出或意外斷線，5秒後準備重新連線...")
        await asyncio.sleep(5) # 給予一點緩衝時間避免連線衝突
        await connect_to_vc()

# 啟動 Web 伺服器防休眠
keep_alive()

# 啟動機器人 (強烈建議將 Token 放在環境變數中)
# 替換 "YOUR_BOT_TOKEN" 或使用環境變數 os.environ.get("TOKEN")
TOKEN = os.environ.get("TOKEN") or "請填入你的機器人Token"
bot.run(TOKEN)
