import pandas as pd
import io
from datetime import datetime
import bot
import discord
from services.db import expenses

async def generate_channel_excel_buffer(channel):
    data = list(expenses.find(
        {"channel_id": channel.id},
        {"user_id": 1, "amount": 1, "note": 1, "timestamp": 1}
    ).sort("timestamp", 1))

    if not data:
        return None

    formatted = []

    for entry in data:
        member = channel.guild.get_member(entry["user_id"]) or await channel.guild.fetch_member(entry["user_id"])
        username = member.display_name if member else "Unknown"

        amount = entry["amount"]

        timestamp = entry["timestamp"]
        if isinstance(timestamp, datetime):
            timestamp = timestamp.strftime("%d-%m-%Y %H:%M")

        formatted.append({
            "Timestamp": timestamp,
            "User": username,
            "Amount": amount,
            "Note": entry["note"]
        })

    df = pd.DataFrame(formatted)

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    return buffer


async def generate_user_excel_buffer(bot, user):
    data = list(expenses.find(
        {"user_id": user.id},
        {"channel_id": 1, "amount": 1, "note": 1, "timestamp": 1}
    ).sort("timestamp", 1))

    if not data:
        return None

    formatted = []

    for entry in data:
        amount = entry.get("amount", 0)
        note = entry.get("note", "")
        timestamp = entry.get("timestamp", "")
        channel_id = entry.get("channel_id")

        if isinstance(timestamp, datetime):
            timestamp = timestamp.strftime("%d-%m-%Y %H:%M")

        try:
            channel = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            channel = None

        channel_name = "DM" if isinstance(channel, discord.DMChannel) else getattr(channel, "name", "Unknown Channel")

        formatted.append({
            "Timestamp": timestamp,
            "Amount": amount,
            "Note": note,
            "Source Channel": channel_name
        })

    df = pd.DataFrame(formatted)

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    return buffer