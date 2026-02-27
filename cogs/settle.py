from discord.ext import commands
from services.expense_service import get_channel_expenses
from services.settlement_service import calculate_settlements

class Settle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def settle(self, ctx):
        expenses = get_channel_expenses(ctx.channel.id)
        settlements = calculate_settlements(expenses)

        if not settlements:
            await ctx.reply("No settlements needed.")
            return

        caller_id = ctx.author.id

        caller_dues = [
            s for s in settlements if s[0] == caller_id
        ]

        if not caller_dues:
            await ctx.reply(f"{ctx.author.mention} you are settled up ✅")
            return

        lines = []

        for debtor_id, creditor_id, amount in caller_dues:
            creditor = ctx.guild.get_member(creditor_id)

            creditor_mention = (
                creditor.mention if creditor else str(creditor_id)
            )

            lines.append(
                f"{ctx.author.mention} → {creditor_mention}: {amount:.2f}"
            )

        await ctx.reply("\n".join(lines))

async def setup(bot):
    await bot.add_cog(Settle(bot))