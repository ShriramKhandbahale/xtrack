from discord.ext import commands
import discord
from datetime import datetime, timezone
from services.export_service import generate_channel_excel_buffer, generate_user_excel_buffer


class Download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def download(self, ctx):
        await ctx.typing()

        try:
            if ctx.guild is None:
                buffer = generate_user_excel_buffer(ctx.author)
                filename = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d_xtrack')}.xlsx"
            else:
                buffer = generate_channel_excel_buffer(ctx.channel)
                filename = f"{ctx.channel.name}_xtrack.xlsx"

            if buffer is None:
                await ctx.reply("No data found.")
                return

            await ctx.reply(file=discord.File(buffer, filename=filename))

        except Exception as e:
            await ctx.reply(f"Error: {e}")

async def setup(bot):
    await bot.add_cog(Download(bot))