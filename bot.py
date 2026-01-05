import time
import sqlite3
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatMemberHandler, ContextTypes

TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"
CHANNEL_ID = -1001234567890  # آیدی عددی کانال

conn = sqlite3.connect("members.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    user_id INTEGER PRIMARY KEY,
    join_date TEXT
)
""")
conn.commit()

async def track_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.chat_member
    user_id = member.from_user.id

    if member.new_chat_member.status == "member":
        cursor.execute(
            "INSERT OR REPLACE INTO members VALUES (?, ?)",
            (user_id, datetime.now().isoformat())
        )
        conn.commit()

async def check_expired(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    cursor.execute("SELECT user_id, join_date FROM members")
    for user_id, join_date in cursor.fetchall():
        if now - datetime.fromisoformat(join_date) > timedelta(days=30):
            try:
                await context.bot.ban_chat_member(CHANNEL_ID, user_id)
                cursor.execute("DELETE FROM members WHERE user_id=?", (user_id,))
                conn.commit()
            except:
                pass

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(ChatMemberHandler(track_members, ChatMemberHandler.CHAT_MEMBER))
app.job_queue.run_repeating(check_expired, interval=86400, first=10)

app.run_polling()
