import os
import asyncio
import datetime
import pytz
import psutil
import time
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

load_dotenv()

start_time = time.time()

app = Client(name="st_userbot",
             api_id=int(os.getenv("API_ID")),
             api_hash=os.getenv("API_HASH"),
             session_string=os.getenv("SESSION_STRING"))

bot = Client(name="st_bot",
             api_id=int(os.getenv("API_ID")),
             api_hash=os.getenv("API_HASH"),
             bot_token=os.getenv("BOT_TOKEN"))

BOT_LIST = [x.strip() for x in os.getenv("BOT_LIST").split(' ')]
CHANNEL_OR_GROUP_ID = int(os.getenv("CHANNEL_OR_GROUP_ID"))
MESSAGE_ID = int(os.getenv("MESSAGE_ID"))
TIME_ZONE = os.getenv("TIME_ZONE")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot.start()


def time_formatter(milliseconds):
    minutes, seconds = divmod(int(milliseconds / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (((str(weeks) + "w:") if weeks else "") +
           ((str(days) + "d:") if days else "") +
           ((str(hours) + "h:") if hours else "") +
           ((str(minutes) + "m:") if minutes else "") +
           ((str(seconds) + "s") if seconds else ""))
    if not tmp:
        return "0s"
    if tmp.endswith(":"):
        return tmp[:-1]
    return tmp


async def main():
    print("Status Checker Bot Started")
    async with app:
        while True:
            TEXT = "This is the live bot status of all Bots 🤖"
            for bots in BOT_LIST:
                ok = await app.get_users(f"@{bots}")
                try:
                    await app.send_message(bots, "/start")
                    await asyncio.sleep(2)
                    messages = app.get_chat_history(bots, limit=1)
                    async for x in messages:
                        msg = x.text
                    if msg == "/start":
                        TEXT += f"\n\n**🤖-[{ok.first_name}](tg://openmessage?user_id={ok.id}): OFFLINE** 💀"
                        await bot.send_message(OWNER_ID, f'Alert {ok.first_name} is offline 💀')
                        await app.read_chat_history(bots)
                    else:
                        TEXT += f"\n\n**🤖-[{ok.first_name}](tg://openmessage?user_id={ok.id}): {msg}**"
                        await app.read_chat_history(bots)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
            time = datetime.datetime.now(pytz.timezone(f"{TIME_ZONE}"))
            date = time.strftime("%d %b %Y")
            time = time.strftime("%I:%M: %p")
            TEXT += f"\n\n--Last checked on--: \n{date}\n{time} ({TIME_ZONE})\n\n**Refreshes Automatically After Every 15 Min.**"
            await bot.edit_message_text(int(CHANNEL_OR_GROUP_ID), MESSAGE_ID, TEXT)
            await asyncio.sleep(900)


@bot.on_message(filters.command('statusbot') & filters.private)
async def activevc(_, message: Message):
    uptime = time_formatter((time.time() - start_time) * 1000)
    cpu = psutil.cpu_percent()
    TEXT = f"UPTIME: {uptime} | CPU: {cpu}%"
    await message.reply(TEXT)


bot.run(main())
