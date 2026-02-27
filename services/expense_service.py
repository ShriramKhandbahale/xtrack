from datetime import datetime, timezone
from services.db import expenses

def record_expense(channel_id, user_id, message_id, amount, note, expense_type="channel"):
    try:
        expenses.insert_one({
            "channel_id": channel_id,
            "user_id": user_id,
            "message_id": message_id,
            "amount": float(amount),
            "note": note,
            "type": expense_type,
            "timestamp": datetime.now(timezone.utc)
        })
        return True
    
    except Exception:
        return False


def update_expense(message_id, user_id, amount, note):
    try:
        result = expenses.update_one(
            {"message_id": message_id, "user_id": user_id},
            {"$set": { "amount": float(amount),"note": note,"timestamp": datetime.now(timezone.utc)  }  }
        )
        return result.modified_count > 0
    except Exception:
        return False


def delete_expense(message_id, user_id):
    try:
        result = expenses.delete_one({
            "message_id": message_id,
            "user_id": user_id
        })
        return result.deleted_count > 0
    except Exception:
        return False


def get_channel_expenses(channel_id):
    return list(expenses.find({
        "channel_id": channel_id,
        "type": "channel"
    }))


def get_user_expenses(channel_id, user_id):
    return list(expenses.find({
        "channel_id": channel_id,
        "user_id": user_id,
        "type": "channel"
    }))


def get_channel_total(channel_id):
    result = expenses.aggregate([
        { "$match": { "channel_id": channel_id,"type": "channel" } },
        { "$group": { "_id": None, "total": {"$sum": "$amount"} } }
    ])

    data = list(result)
    return float(data[0]["total"]) if data else 0.0


def get_user_total(channel_id, user_id):
    result = expenses.aggregate([
        { "$match": { "channel_id": channel_id, "user_id": user_id, "type": "channel" } },
        { "$group": { "_id": None, "total": { "$sum": "$amount" } } }
    ])

    data = list(result)
    return float(data[0]["total"]) if data else 0.0