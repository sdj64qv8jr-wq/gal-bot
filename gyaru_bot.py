import discord
import google.generativeai as genai
import os
from aiohttp import web
import asyncio

# ===========================
# 設定
# ===========================
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ===========================
# クライアント設定
# ===========================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ===========================
# ギャル変換関数
# ===========================
def convert_to_gyaru(text: str) -> str:
    prompt = (
        "以下のメッセージをギャル語に変換してください。\n"
        "ルール:\n"
        "- 「マジ」「やばい」「うける」「ちょー」などのギャル語を使う\n"
        "- 語尾に「～じゃん」「～じゃなくない？」「～だし」などをつける\n"
        "- 絵文字を適度に使う（💅✨🥺💕など）\n"
        "- 意味はそのままに、口調だけギャルにする\n"
        "- 変換結果だけ返して。説明は不要。\n\n"
        f"変換するメッセージ:\n{text}"
    )
    response = model.generate_content(prompt)
    return response.text

# ===========================
# Renderがスリープしないようにするサーバー
# ===========================
async def health_check(request):
    return web.Response(text="OK")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()

# ===========================
# イベント
# ===========================
@client.event
async def on_ready():
    print(f"✅ ログイン成功: {client.user}")

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if not message.content.strip():
        return

    try:
        gyaru_text = convert_to_gyaru(message.content)
        await message.reply(gyaru_text)
    except Exception as e:
        print(f"エラー: {e}")
        await message.reply("ちょーごめん、なんかエラーでたんだけど💦")

# ===========================
# 起動
# ===========================
async def main():
    await start_web_server()
    await client.start(DISCORD_TOKEN)

asyncio.run(main())
