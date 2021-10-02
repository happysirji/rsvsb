import os
import sys
import asyncio
from config import Config
from logger import LOGGER
from utils import update, is_admin
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaDocument


HOME_TEXT = "👋🏻 **Hi [{}](tg://user?id={})**, \n\nI'm **RS Video Player Bot**. \nI Can Stream Lives, YouTube Videos & Telegram Video Files On Voice Chat Of Telegram Channels & Groups."
HELP_TEXT = """
🏷️ --**Setting Up**-- :

\u2022 Add the bot and user account in your group with admin rights.
\u2022 Start a voice chat in your group & restart the bot if not joined to vc.
\u2022 Use /pl [video name] or use /pl as a reply to an video file or youtube link.

🏷️ --**Common Commands**-- :

\u2022 `/start` - start the bot
\u2022 `/usage` - shows the help
\u2022 `/pl` - plays the video
\u2022 `/playlist` - shows the playlist

🏷️ --**Admins Commands**-- :

\u2022 `/seek` - seek the video
\u2022 `/next` - skip current video
\u2022 `/stream` - start live stream
\u2022 `/ps` - pause playing video
\u2022 `/rs` - resume playing video
\u2022 `/m` - mute the vc userbot
\u2022 `/unm` - unmute the vc userbot
\u2022 `/le` - leave the voice chat
\u2022 `/shuffle` - shuffle the playlist
\u2022 `/volume` - change volume (0-200)
\u2022 `/repeat` - play from the beginning
\u2022 `/clr` - clear the playlist queue
\u2022 `/reboot` - update & restart the bot
\u2022 `/setvar` - set/change heroku configs
\u2022 `/getlogs` - get the ffmpeg & bot logs
"""

admin_filter=filters.create(is_admin) 

@Client.on_message(filters.command(["start", f"start@{Config.BOT_USERNAME}"]))
async def start(client, message):
    buttons = [
            [
                InlineKeyboardButton("SEARCH INLINE", switch_inline_query_current_chat=""),
            ],
            [
                InlineKeyboardButton("CHANNEL", url="https://t.me/rsbro"),
                InlineKeyboardButton("GROUP", url="https://t.me/joinchat/_8Tt7Srw5MQ4YTNl"),
            ],
            [
                InlineKeyboardButton("❔ HOW TO USE ❔", callback_data="usage"),
            ]
            ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(HOME_TEXT.format(message.from_user.first_name, message.from_user.id), reply_markup=reply_markup)


@Client.on_message(filters.command(["usage", f"usage@{Config.BOT_USERNAME}"]))
async def show_help(client, message):
    buttons = [
            [
                InlineKeyboardButton("CHANNEL", url="https://t.me/rsbro"),
                InlineKeyboardButton("GROUP", url="https://t.me/joinchat/_8Tt7Srw5MQ4YTNl"),
            ],
            [
                InlineKeyboardButton("BACK HOME", callback_data="home"),
                InlineKeyboardButton("CLOSE MENU", callback_data="close"),
            ]
            ]
    reply_markup = InlineKeyboardMarkup(buttons)
    if Config.msg.get('usage') is not None:
        await Config.msg['usage'].delete()
    Config.msg['usage'] = await message.reply_text(
        HELP_TEXT,
        reply_markup=reply_markup
        )


@Client.on_message(filters.command(["reboot", "update", f"reboot@{Config.BOT_USERNAME}", f"update@{Config.BOT_USERNAME}"]) & admin_filter)
async def update_handler(client, message):
    if Config.HEROKU_APP:
        k=await message.reply_text("🔄 **Heroku Detected, \nRestarting App To Update!**")
    else:
        k=await message.reply_text("🔄 **Restarting ...**")
    await update()
    try:
        await k.edit("✅ **Restarted Successfully!**")
    except:
        pass


@Client.on_message(filters.command(["getlogs", f"getlogs@{Config.BOT_USERNAME}"]) & admin_filter)
async def get_logs(client, message):
    logs=[]
    if os.path.exists("ffmpeg.txt"):
        logs.append(InputMediaDocument("ffmpeg.txt", caption="FFMPEG Logs"))
    if os.path.exists("ffmpeg.txt"):
        logs.append(InputMediaDocument("botlog.txt", caption="RS Video Player Logs"))
    if logs:
        try:
            await message.reply_media_group(logs)
        except:
            await message.reply_text("❌ **An Error Occoured !**")
            pass
        logs.clear()
    else:
        await message.reply_text("❌ **No Log Files Found !**")


@Client.on_message(filters.command(["setvar", f"setvar@{Config.BOT_USERNAME}"]) & admin_filter)
async def set_heroku_var(client, message):
    if not Config.HEROKU_APP:
        buttons = [[InlineKeyboardButton('HEROKU_API_KEY', url='https://dashboard.heroku.com/account/applications/authorizations/new')]]
        await message.reply_text(
            text="❗ **No Heroku App Found !** \n__Please Note That, This Command Needs The Following Heroku Vars To Be Set :__ \n\n1. `HEROKU_API_KEY` : Your heroku account api key.\n2. `HEROKU_APP_NAME` : Your heroku app name.", 
            reply_markup=InlineKeyboardMarkup(buttons))
        return     
    if " " in message.text:
        cmd, env = message.text.split(" ", 1)
        if  not "=" in env:
            return await message.reply_text("❗ **You Should Specify The Value For Variable!** \n\nFor Example: \n`/setvar CHAT_ID=-1000000000001`")
        var, value = env.split("=", 2)
        config = Config.HEROKU_APP.config()
        if not value:
            m=await message.reply_text(f"❗ **No Value Specified, So Deleting `{var}` Variable !**")
            await asyncio.sleep(2)
            if var in config:
                del config[var]
                await m.edit(f"🗑 **Sucessfully Deleted `{var}` !**")
                config[var] = None
            else:
                await m.edit(f"🤷‍♂️ **Variable Named `{var}` Not Found, Nothing Was Changed !**")
            return
        if var in config:
            m=await message.reply_text(f"⚠️ **Variable Already Found, So Edited Value To `{value}` !**")
        else:
            m=await message.reply_text(f"⚠️ **Variable Not Found, So Setting As New Var !**")
        await asyncio.sleep(2)
        await m.edit(f"✅ **Succesfully Set Variable `{var}` With Value `{value}`, Now Restarting To Apply Changes !**")
        config[var] = str(value)
    else:
        await message.reply_text("❗ **You Haven't Provided Any Variable, You Should Follow The Correct Format !** \n\nFor Example: \n• `/setvar CHAT_ID=-1000000000001` to change or set CHAT_ID var. \n• `/setvar REPLY_MESSAGE=` to delete REPLY_MESSAGE var.") 
