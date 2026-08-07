import discord
from discord.ext import commands, tasks
import os
import asyncio
from keep_alive import keep_alive

# 你的語音頻道 ID
TARGET_VC_ID = 1449627369672540170

intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 用來防止重複觸發重連的鎖
is_reconnecting = False

async def connect_to_vc():
    """負責連線到指定語音頻道的函式"""
    global is_reconnecting
    await bot.wait_until_ready()
    await asyncio.sleep(3) # 給予緩衝時間避免過快交握
    
    channel = bot.get_channel(TARGET_VC_ID)
    if not channel:
        print("❌ 找不到指定的語音頻道！")
        is_reconnecting = False
        return
    
    for voice in list(bot.voice_clients):
        try:
            await voice.disconnect(force=True)
        except Exception:
            pass

    try:
        # 增加 timeout 避免伺服器回應太慢直接爆錯
        await asyncio.wait_for(channel.connect(), timeout=15.0)
        print(f"✅ 成功加入語音頻道：{channel.name}")
    except Exception as e:
        print(f"⚠️ 連線失敗，將在一段時間後重試：{e}")
        # 連線失敗時，強制清理殘留物件
        for voice in list(bot.voice_clients):
            try:
                await voice.disconnect(force=True)
            except:
                pass
    finally:
        is_reconnecting = False

@bot.event
async def on_ready():
    print(f"🤖 登入成功：{bot.user}")
    activity = discord.Activity(type=discord.ActivityType.watching, name="🌌 今晚的星空")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    bot.loop.create_task(connect_to_vc())
    
    if not check_connection.is_running():
        check_connection.start()

@tasks.loop(minutes=5)
async def check_connection():
    """每 5 分鐘主動檢查一次連線狀態"""
    global is_reconnecting
    if is_reconnecting:
        return
    channel = bot.get_channel(TARGET_VC_ID)
    if channel:
        voice = discord.utils.get(bot.voice_clients, guild=channel.guild)
        if not voice or not voice.is_connected():
            print("🔄 檢查到未連線，正在重新導向...")
            is_reconnecting = True
            await connect_to_vc()

@bot.event
async def on_voice_state_update(member, before, after):
    """嚴格防呆監聽：加入 Lock 機制防止重複觸發"""
    global is_reconnecting
    if member == bot.user:
        if after.channel is not None:
            return
        
        if before.channel is not None and after.channel is None:
            if is_reconnecting:
                return  # 如果已經在重新連線中了，直接忽略這次觸發
            
            is_reconnecting = True
            print("⚡ 機器人被移出或意外斷線，5秒後準備重新連線...")
            await asyncio.sleep(5)
            await connect_to_vc()

# 啟動 Web 伺服器防休眠
keep_alive()

# 啟動機器人
TOKEN = os.environ.get("TOKEN")
bot.run(TOKEN)
