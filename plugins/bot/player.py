import os
import re
import asyncio
from config import Config
from logger import LOGGER
from datetime import datetime
from youtube_dl import YoutubeDL
from pyrogram.types import Message
from pyrogram import Client, filters
from youtube_search import YoutubeSearch
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import delete, download, get_admins, is_admin, get_buttons, get_link, leave_call, play, get_playlist_str, send_playlist, shuffle_playlist, start_stream, stream_from_link

admin_filter=filters.create(is_admin)


@Client.on_message(filters.command(["pl", f"pl@{Config.BOT_USERNAME}"]) & (filters.chat(Config.CHAT_ID) | filters.private | filters.chat(Config.LOG_GROUP)))
async def add_to_playlist(_, message: Message):
    if Config.ADMIN_ONLY == "True":
        admins = await get_admins(Config.CHAT_ID)
        if message.from_user.id not in admins:
            k=await message.reply_sticker("CAACAgUAAxkBAAEKyK5g6uADBoD3OZj6uEScTrK_P6w5PAACrgMAAkHwWVeAN1UFDSxiPyAE")
            await delete(k)
            return
    type=""
    yturl=""
    ysearch=""
    if message.reply_to_message and message.reply_to_message.video:
        msg = await message.reply_text("⚡️")
        type='video'
        m_video = message.reply_to_message.video       
    elif message.reply_to_message and message.reply_to_message.document:
        msg = await message.reply_text("⚡️")
        m_video = message.reply_to_message.document
        type='video'
        if not "video" in m_video.mime_type:
            k=await msg.edit("⛔️ **Invalid Video File Provided !**")
            await delete(k)
            return
    else:
        if message.reply_to_message:
            link=message.reply_to_message.text
            regex = r"^(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?"
            match = re.match(regex,link)
            if match:
                type="youtube"
                yturl=link
        elif " " in message.text:
            text = message.text.split(" ", 1)
            query = text[1]
            regex = r"^(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?"
            match = re.match(regex,query)
            if match:
                type="youtube"
                yturl=query
            else:
                type="query"
                ysearch=query
        else:
            k=await message.reply_text("❗ __**Send Me A YouTube Video Name / YouTube Video Link / Reply To Video To Play In Telegram Video Chat !**__")
            await delete(k)
            return
    user=f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    if type=="video":
        now = datetime.now()
        nyav = now.strftime("%d-%m-%Y-%H:%M:%S")
        data={1:m_video.file_name, 2:m_video.file_id, 3:"telegram", 4:user, 5:f"{nyav}_{m_video.file_size}"}
        Config.playlist.append(data)
        await msg.edit("➕ **Media Added To Playlist !**")
    if type=="youtube" or type=="query":
        if type=="youtube":
            msg = await message.reply_text("🔎")
            url=yturl
        elif type=="query":
            try:
                msg = await message.reply_text("🔎")
                ytquery=ysearch
                results = YoutubeSearch(ytquery, max_results=1).to_dict()
                url = f"https://youtube.com{results[0]['url_suffix']}"
                title = results[0]["title"][:40]
            except Exception as e:
                k=await msg.edit(
                    "**Nothing Found !\nTry Searching in Inline Mode 😉!**"
                )
                LOGGER.error(str(e))
                await delete(k)
                return
        else:
            return
        ydl_opts = {
            "geo-bypass": True,
            "nocheckcertificate": True
        }
        ydl = YoutubeDL(ydl_opts)
        try:
            info = ydl.extract_info(url, False)
        except Exception as e:
            LOGGER.error(e)
            k=await msg.edit(
                f"❌ **YouTube Download Error !** \n\n{e}"
                )
            LOGGER.error(str(e))
            await delete(k)
            return
        title = info["title"]
        now = datetime.now()
        nyav = now.strftime("%d-%m-%Y-%H:%M:%S")
        data={1:title, 2:url, 3:"youtube", 4:user, 5:f"{nyav}_{message.from_user.id}"}
        Config.playlist.append(data)
        await msg.edit(f"➕ **[{title}]({url}) Added To Playlist !**", disable_web_page_preview=True)
    if len(Config.playlist) == 1:
        m_status = await msg.edit("⚡️")
        await download(Config.playlist[0], m_status)
        await m_status.delete()
        await m_status.reply_to_message.delete()
        await play()
    else:
        await send_playlist()
        await delete(msg)
    pl=await get_playlist_str()
    if message.chat.type == "private":
        await message.reply_text(pl, reply_markup=await get_buttons() ,disable_web_page_preview=True)        
    elif not Config.LOG_GROUP and message.chat.type == "supergroup":
        await message.reply_text(pl, disable_web_page_preview=True, reply_markup=await get_buttons())          
    for track in Config.playlist[:2]:
        await download(track)

@Client.on_message(filters.command(["j", f"j@{Config.BOT_USERNAME}"]) & admin_filter & (filters.chat(Config.CHAT_ID) | filters.private | filters.chat(Config.LOG_GROUP)))
async def join_voice_chat(_, m: Message):
    if not Config.CALL_STATUS:
        await start_stream()
    k=await m.reply_text("✅ **Joined Video Chat !**")
    await delete(k)
    
@Client.on_message(filters.command(["le", f"le@{Config.BOT_USERNAME}"]) & admin_filter & (filters.chat(Config.CHAT_ID) | filters.private | filters.chat(Config.LOG_GROUP)))
async def leave_voice_chat(_, m: Message):
    if not Config.CALL_STATUS:
        k=await m.reply_text("🤖 **Didn't Joined Video Chat !**")
        await delete(k)
        return
    await leave_call()
    k=await m.reply_text("✅ **Left Video Chat !**")
    await delete(k)


@Client.on_message(filters.command(["shuffle", f"shuffle@{Config.BOT_USERNAME}"]) & admin_filter & (filters.chat(Config.CHAT_ID) | filters.private | filters.chat(Config.LOG_GROUP)))
async def shuffle_play_list(client, m: Message):
    if not Config.CALL_STATUS:
        k=await m.reply_text("🤖 **Didn't Joined Video Chat !**")
        await delete(k)
    else:
        if len(Config.playlist) > 2:
            await shuffle_playlist()
            k=await m.reply_text(f"🔄 **Playlist Shuffled !**")
            await delete(k)
        else:
            k=await m.reply_text(f"⛔️ **Can't Shuffle Playlist For Less Than 3 Video !**")
            await delete(k)


@Client.on_message(filters.command(["clr", f"clr@{Config.BOT_USERNAME}"]) & admin_filter & (filters.chat(Config.CHAT_ID) | filters.private | filters.chat(Config.LOG_GROUP)))
async def clear_play_list(client, m: Message):
    if not Config.CALL_STATUS:
        k=await m.reply_text("🤖 **Didn't Joined Video Chat !**")
        await delete(k)
        return
    if not Config.playlist:
        k=await m.reply_text("⛔️ **Empty Playlist !**")
        await delete(k)
        return
    Config.playlist.clear()   
    k=await m.reply_text(f"✅ **Playlist Cleared !**")
    await delete(k)
    await start_stream()


@Client.on_message(filters.command(["stream", f"stream@{Config.BOT_USERNAME}"]) & admin_filter & (filters.chat(Config.CHAT_ID) | filters.private | filters.chat(Config.LOG_GROUP)))
async def stream(client, m: Message):
    if m.reply_to_message:
        link=m.reply_to_message.text
    elif " " in m.text:
        text = m.text.split(" ", 1)
        link = text[1]
    else:
        k=await m.reply_text("❗ __**Send Me A Live Stream Link / YouTube Live Stream Link To Start Live Streaming !**__")
        await delete(k)
        return
    regex = r"^(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?"
    match = re.match(regex,link)
    if match:
        stream_link=await get_link(link)
        if not stream_link:
            k=await m.reply_text("⛔️ **Invalid Stream Link Given !**")
            await delete(k)
            return
    else:
        stream_link=link
    k, msg=await stream_from_link(stream_link)
    if k == False:
        s=await m.reply_text(msg)
        await delete(s)
        return
    s=await m.reply_text(f"▶️ **Started [Live Streaming]({stream_link}) !**", disable_web_page_preview=True)
    await delete(s)


admincmds=["j", "le", "ps", "rs", "next", "reboot", "volume", "shuffle", "clr", "update", "repeat", "getlogs", "stream", "m", "unm", "seek", f"m@{Config.BOT_USERNAME}", f"unm@{Config.BOT_USERNAME}", f"seek@{Config.BOT_USERNAME}", f"stream@{Config.BOT_USERNAME}", f"getlogs@{Config.BOT_USERNAME}", f"reboot@{Config.BOT_USERNAME}", f"j@{Config.BOT_USERNAME}", f"le@{Config.BOT_USERNAME}", f"ps@{Config.BOT_USERNAME}", f"rs@{Config.BOT_USERNAME}", f"next@{Config.BOT_USERNAME}", f"reboot@{Config.BOT_USERNAME}", f"volume@{Config.BOT_USERNAME}", f"shuffle@{Config.BOT_USERNAME}", f"clr@{Config.BOT_USERNAME}", f"update@{Config.BOT_USERNAME}"]

@Client.on_message(filters.command(admincmds) & ~admin_filter & (filters.chat(Config.CHAT_ID) | filters.private | filters.chat(Config.LOG_GROUP)))
async def notforu(_, m: Message):
    k=await _.send_cached_media(chat_id=m.chat.id, file_id="CAACAgUAAxkBAAEKyK5g6uADBoD3OZj6uEScTrK_P6w5PAACrgMAAkHwWVeAN1UFDSxiPyAE", caption="**You Are Not Authorized !!**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Join Here', url='https://t.me/rsbro')]]), reply_to_message_id=m.message_id)
    await delete(k)

allcmd = ["pl", "playlist", f"pl@{Config.BOT_USERNAME}", f"playlist@{Config.BOT_USERNAME}"] + admincmds

@Client.on_message(filters.command(allcmd) & filters.group & ~(filters.chat(Config.CHAT_ID) | filters.private | filters.chat(Config.LOG_GROUP)))
async def not_chat(_, m: Message):
    buttons = [
            [
                InlineKeyboardButton("CHANNEL", url="https://t.me/rsbro"),
                InlineKeyboardButton("GROUP", url="https://t.me/joinchat/_8Tt7Srw5MQ4YTNl"),
            ]
         ]
    await m.reply_text(text="**Sorry, You Can't Use This Bot In This Group 🤷‍♂️!")