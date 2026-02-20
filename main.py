import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import httpx
import server

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = os.getenv("GAS_API_EP")

handler = logging.FileHandler(
    filename="discord.log",
    encoding="utf-8",
    mode="w"
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print(f"{bot.user.name} initialized")

@bot.command()
async def rec(ctx, *, msg: str = None):
    if not msg:
        await ctx.send("format: `!rec amount, note`")
        return

    amount_str, note = msg.split(",", 1)
    amount = float(amount_str.strip())
    note = note.strip()

    payload = {
        "amount": amount,
        "note": note,
        "paid_by": ctx.author.display_name
    }

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        response = await client.post(API_URL, json=payload)

    if response.status_code in (200, 201):
        await ctx.message.add_reaction("✅")
    else:
        await ctx.message.add_reaction("❌")


@bot.command()
async def total(ctx):
    async with httpx.AsyncClient(
        timeout=10.0,
        follow_redirects=True
    ) as client:
        response = await client.get(API_URL)

    if response.status_code != 200:
        await ctx.message.add_reaction("❌")
        return

    res = response.json()

    data = res.get("data", [])
    total_amount = 0.0

    for entry in data:
        try:
            total_amount += float(entry.get("amount", 0))
        except (ValueError, TypeError):
            pass

    await ctx.reply(
        f"{total_amount:.2f}"
    )

@bot.command()
async def settle(ctx):
    caller = ctx.author.display_name
    guild = ctx.guild

    async with httpx.AsyncClient(
        timeout=10.0,
        follow_redirects=True
    ) as client:
        response = await client.get(API_URL)

    if response.status_code != 200:
        await ctx.message.add_reaction("❌")
        return

    res = response.json()
    data = res.get("data", [])

    totals = {}
    total_expense = 0.0

    for entry in data:
        amount = float(entry.get("amount", 0))
        user = entry.get("paid_by")

        total_expense += amount
        totals[user] = totals.get(user, 0) + amount

    participants = list(totals.keys())
    num_people = len(participants)

    if num_people == 0:
        await ctx.message.add_reaction("❌")
        return

    share = total_expense / num_people

    balances = {
        user: totals[user] - share
        for user in participants
    }

    creditors = []
    debtors = []

    for user, balance in balances.items():
        if balance > 0:
            creditors.append([user, balance])
        elif balance < 0:
            debtors.append([user, balance])

    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1])

    settlements = []

    i = j = 0

    while i < len(debtors) and j < len(creditors):
        debtor_user, debtor_amt = debtors[i]
        creditor_user, creditor_amt = creditors[j]

        amount_to_pay = min(-debtor_amt, creditor_amt)

        settlements.append(
            (debtor_user, creditor_user, round(amount_to_pay, 2))
        )

        debtors[i][1] += amount_to_pay
        creditors[j][1] -= amount_to_pay

        if abs(debtors[i][1]) < 0.01:
            i += 1
        if abs(creditors[j][1]) < 0.01:
            j += 1

    caller_dues = [
        s for s in settlements if s[0] == caller
    ]

    if not caller_dues:
        await ctx.reply(f"{ctx.author.mention} you are settled up")
        return

    message_lines = []

    for debtor, creditor, amount in caller_dues:

        debtor_member = discord.utils.find(
            lambda m: m.display_name == debtor,
            guild.members
        )

        creditor_member = discord.utils.find(
            lambda m: m.display_name == creditor,
            guild.members
        )

        debtor_mention = debtor_member.mention if debtor_member else debtor
        creditor_mention = creditor_member.mention if creditor_member else creditor

        message_lines.append(
            f"{debtor_mention} → {creditor_mention}: {amount:.2f}"
        )

    await ctx.reply("\n".join(message_lines))

server.keep_alive()
bot.run(TOKEN, log_handler=handler, log_level=logging.INFO)