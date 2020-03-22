from cs50 import SQL

db = SQL("sqlite:///receipt.db")
receipts = db.execute("SELECT name, head, total, date, date_created, category, language, image_link FROM 'receipts' WHERE user_id = :user_id", user_id=1)
print(receipts)