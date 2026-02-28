from discord.ext import commands
from services.expense_service import (
    record_expense,
    get_channel_total,
    get_user_total,
    update_expense,
    delete_expense
)

class Expense(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rec(self, ctx, *, input_text: str):
        try:
            if "," not in input_text:
                await ctx.send("Format: `$rec amount, note`")
                return

            amount_part, note = input_text.split(",", 1)
            amount = float(amount_part.strip())
            note = note.strip()

            if amount <= 0:
                await ctx.message.add_reaction("🙅")
                return

            record_expense(
                ctx.channel.id,
                ctx.author.id,
                ctx.message.id,
                amount,
                note,
            )

            await ctx.message.add_reaction("✅")

        except Exception:
            await ctx.message.add_reaction("❌")

    @commands.command()
    async def total(self, ctx):
        await ctx.typing()
        total = get_channel_total(ctx.channel.id)
        await ctx.reply(f"Total: {total:.2f}")

    @commands.command()
    async def mytotal(self, ctx):
        await ctx.typing()
        total = get_user_total(ctx.channel.id, ctx.author.id)
        await ctx.reply(f"Your total: {total:.2f}")
        
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return

        if not after.content.lower().startswith("$rec"):
            return

        try:
            input_text = after.content[4:].strip()

            if "," not in input_text:
                return

            amount_part, note = input_text.split(",", 1)
            amount = float(amount_part.strip())
            note = note.strip()

            updated = update_expense(
                before.id,
                before.author.id,
                amount,
                note
            )

            if updated:
                await after.add_reaction("✏️")

        except Exception:
            await after.add_reaction("❌")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        delete_expense(
            message.id,
            message.author.id
        )


async def setup(bot):
    await bot.add_cog(Expense(bot))