import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer as MinecraftServer
from PIL import Image, ImageDraw, ImageFont
import io
import os

# 봇 토큰, 섭링, 채널
TOKEN = '봇토큰'
SERVER_ADDRESS = '마크 섭링'
CHANNEL_ID = 디코 채널 ID

# 봇설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

last_message_id = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    check_server_status.start()

@tasks.loop(minutes=5)  # 5분마다 서버 상태 확인
async def check_server_status():
    global last_message_id
    channel = bot.get_channel(CHANNEL_ID)

    try:
        # 서버 상태 확인
        server = MinecraftServer.lookup(SERVER_ADDRESS)
        status = server.status()
        players = status.players.sample  # 현재 접속한 플레이어 목록

        # 이미지 생성
        img = Image.new('RGB', (400, 250), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # 폰트 설정
        font = ImageFont.truetype(r"폰트저장위치", 14)

        # 서버 기본 정보
        draw.text((10, 10), f"서버 주소: {SERVER_ADDRESS}", fill=(0, 0, 0), font=font)
        draw.text((10, 40), f"상태: 온라인", fill=(0, 128, 0), font=font)
        draw.text((10, 70), f"현재 인원: {status.players.online}/{status.players.max}", fill=(0, 0, 0), font=font)
        draw.text((10, 100), f"핑: {status.latency} ms", fill=(0, 0, 0), font=font)

        # 접속 중인 플레이어 목록
        if players:
            draw.text((10, 130), "접속 중인 플레이어:", fill=(0, 0, 0), font=font)
            for i, player in enumerate(players):
                draw.text((20, 150 + i * 20), player.name, fill=(0, 0, 0), font=font)
        else:
            draw.text((10, 130), "접속 중인 플레이어가 없습니다.", fill=(128, 128, 128), font=font)

        # 이미지 전송, 수정
        with io.BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            
            if last_message_id:
                try:
                    old_message = await channel.fetch_message(last_message_id)
                    await old_message.edit(attachments=[])
                    await old_message.edit(attachments=[discord.File(fp=image_binary, filename="server_status.png")])
                except discord.errors.NotFound:
                    new_message = await channel.send(file=discord.File(fp=image_binary, filename="server_status.png"))
                    last_message_id = new_message.id
            else:
                new_message = await channel.send(file=discord.File(fp=image_binary, filename="server_status.png"))
                last_message_id = new_message.id

    except Exception as e:
        # 서버 오프일때
        img = Image.new('RGB', (400, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), f"서버 주소: {SERVER_ADDRESS}", fill=(0, 0, 0), font=font)
        draw.text((10, 40), "상태: 오프라인", fill=(255, 0, 0), font=font)

        with io.BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            
            if last_message_id:
                try:
                    old_message = await channel.fetch_message(last_message_id)
                    await old_message.edit(attachments=[])
                    await old_message.edit(attachments=[discord.File(fp=image_binary, filename="server_status_offline.png")])
                except discord.errors.NotFound:
                    new_message = await channel.send(file=discord.File(fp=image_binary, filename="server_status_offline.png"))
                    last_message_id = new_message.id
            else:
                new_message = await channel.send(file=discord.File(fp=image_binary, filename="server_status_offline.png"))
                last_message_id = new_message.id

# 봇 실행
bot.run(TOKEN)
