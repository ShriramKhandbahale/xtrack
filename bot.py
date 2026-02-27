import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import server

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(
    filename="discord.log",
    encoding="utf-8",
    mode="w"
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="$",
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print(f"{bot.user} initialized")

async def load_cogs():
    await bot.load_extension("cogs.expense")
    await bot.load_extension("cogs.settle")
    await bot.load_extension("cogs.download")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

import asyncio
server.keep_alive()
asyncio.run(main())