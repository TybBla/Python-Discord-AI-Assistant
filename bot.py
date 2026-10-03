import discord
from discord.ext import commands
import google.generativeai as genai
from openai import OpenAI
import os
from flask import Flask
from threading import Thread

# Serwer keep-alive dla rendera
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Tokeny
DISCORD_TOKEN = 'TOKEN'
GITHUB_TOKEN = 'TOKEN'
GEMINI_API_KEY = 'KEY'

github_client = OpenAI(base_url="https://models.inference.ai.azure.com", api_key=GITHUB_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def get_ai_response(user_input):
    try:
        response = github_client.chat.completions.create(
            messages=[{"role": "user", "content": user_input}],
            model="Llama-3.3-70B-Instruct",
        )
        return f"[GitHub] {response.choices[0].message.content}"
    except Exception as e:
        print(f"GitHub Error: {e}")
        try:
            response = gemini_model.generate_content(user_input)
            return f"[Gemini Fallback] {response.text}"
        except Exception as e2:
            return "Sorki, oba systemy leżą."

@bot.event
async def on_ready():
    print(f'Bot {bot.user} jest online 24/7!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    async with message.channel.typing():
        odpowiedz = await get_ai_response(message.content)
        await message.channel.send(odpowiedz)

# --- START ---
keep_alive() # odpala serwer WWW w tle
bot.run(DISCORD_TOKEN)
