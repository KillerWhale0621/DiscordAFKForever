import discord
from discord.ext import commands, tasks
import os
import asyncio
from keep_alive import keep_alive

# 你的語音頻道 ID
TARGET_VC_ID = 1449627369672540170

intents = discord.Intents.default()
intents.voice_states = True  # 確保開啟語音狀態監聽權限
bot = commands.Bot(command_prefix="!", intents=intents)

async def connect_to_vc():
    """負責連線到指定語音頻道的函式"""
    await bot.wait_until_ready()
    channel = bot.get_channel(TARGET_VC_ID)
    
    if not channel:
        print("❌ 找不到指定的語音頻道，請檢查 ID 是否正確！")
        return
    
    # 檢查現有的語音連線
    voice = discord.utils.get(bot.voice_clients, guild=channel.guild)
    if voice and voice.is_connected():
        if voice.channel == channel:
            return  # 已經在正確的頻道裡了，不需要重複連
        else:
            await voice.move_to(channel)
            return

    try:
        await channel.connect()
        print(f"✅ 成功加入語音頻道：{channel.name}")
    except Exception as e:
        print(f"⚠️ 連線失敗（稍後會自動重試）：{e}")

@bot.event
async def on_ready():
    print(f"🤖 登入成功：{bot.user}")
    activity = discord.Activity(type=discord.ActivityType.watching, name="🌌 今晚的星空")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    # 啟動時馬上連線
    bot.loop.create_task(connect_to_vc())
    
    if not check_connection.is_running():
        check_connection.start()

@tasks.loop(minutes=5)
async def check_connection():
    """每 5 分鐘主動檢查一次連線狀態"""
    channel = bot.get_channel(TARGET_VC_ID)
    if channel:
        voice = discord.utils.get(bot.voice_clients, guild=channel.guild)
        if not voice or not voice.is_connected():
            print("🔄 檢查到未連線，正在重新導向...")
            await connect_to_vc()

@bot.event
async def on_voice_state_update(member, before, after):
    """防呆監聽：只有當機器人本尊『原本在頻道內』卻被『強行斷開/踢出』時才觸發"""
    if member == bot.user:
        # 如果是自己主動離開或轉移，不動作
        if after.channel is not None:
            return
        # 如果是被踢出或斷線
        if before.channel is not None and after.channel is None:
            print("⚡ 機器人被移出或意外斷線，5秒後準備重新連線...")
            await asyncio.sleep(5)
            await connect_to_vc()

# 啟動 Web 伺服器防休眠
keep_alive()

# 啟動機器人
TOKEN = os.environ.get("TOKEN")
bot.run(TOKEN)
