def calculate_settlements(expenses):
    totals = {}
    total_expense = 0.0

    for entry in expenses:
        amount = float(entry["amount"])
        user = entry["user_id"]

        total_expense += amount
        totals[user] = totals.get(user, 0) + amount

    participants = list(totals.keys())
    if not participants:
        return []

    share = total_expense / len(participants)

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

    return settlements