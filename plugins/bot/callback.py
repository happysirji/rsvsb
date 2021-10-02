from asyncio import sleep
from config import Config
from logger import LOGGER
from pyrogram import Client
from pyrogram.errors import MessageNotModified
from plugins.bot.commands import HOME_TEXT, HELP_TEXT
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils import get_admins, get_buttons, get_playlist_str, mute, pause, restart_playout, resume, seek_file, shuffle_playlist, skip, unmute

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    admins = await get_admins(Config.CHAT_ID)
    if query.from_user.id not in admins and query.data != "usage":
        await query.answer(
            "You're Not Allowed! 🤣",
            show_alert=True
            )
        return
    if query.data.lower() == "shuffle":
        if not Config.playlist:
            await query.answer("⛔️ Empty Playlist !", show_alert=True)
            return
        await shuffle_playlist()
        await query.answer("🔁 Shuffling !", show_alert=True)
        await sleep(1)
        try:
            await query.message.edit_reply_markup(reply_markup=await get_buttons())
        except MessageNotModified:
            pass

    elif query.data.lower() == "ps":
        if Config.PAUSE:
            await query.answer("⏸ Already Paused !", show_alert=True)
        else:
            await pause()
            await query.answer("⏸ Paused !", show_alert=True)
            await sleep(1)
        try:
            await query.message.edit_reply_markup(reply_markup=await get_buttons())
        except MessageNotModified:
            pass
    
    elif query.data.lower() == "rs":   
        if not Config.PAUSE:
            await query.answer("▶️ Already Resumed !", show_alert=True)
        else:
            await resume()
            await query.answer("▶️ Resumed !", show_alert=True)
            await sleep(1)
        try:
            await query.message.edit_reply_markup(reply_markup=await get_buttons())
        except MessageNotModified:
            pass

    elif query.data.lower() == "next":   
        if not Config.playlist:
            await query.answer("⛔️ Empty Playlist !", show_alert=True)
        else:
            await skip()
            await query.answer("⏭ Skipped !", show_alert=True)
            await sleep(1)
        if Config.playlist:
            title=f"▶️ <b>{Config.playlist[0][1]}</b>"
        elif Config.STREAM_LINK:
            title=f"▶️ <b>Streaming [Given URL]({Config.DATA['FILE_DATA']['file']}) !</b>"
        else:
            title=f"▶️ <b>Streaming [Startup Stream]({Config.STREAM_URL}) !</b>"
        try:
            await query.message.edit(f"{title}",
                disable_web_page_preview=True,
                reply_markup=await get_buttons()
            )
        except MessageNotModified:
            pass

    elif query.data.lower() == "rp":
        if not Config.playlist:
            await query.answer("⛔️ Empty Playlist !", show_alert=True)
        else:
            await restart_playout()
            await query.answer("🔂 Replaying !", show_alert=True)
            await sleep(1)
        try:
            await query.message.edit_reply_markup(reply_markup=await get_buttons())
        except MessageNotModified:
            pass

    elif query.data.lower() == "m":
        if Config.MUTED:
            await unmute()
            await query.answer("🔉 Unmuted !", show_alert=True)
        else:
            await mute()
            await query.answer("🔇 Muted !", show_alert=True)
        await sleep(1)
        try:
            await query.message.edit_reply_markup(reply_markup=await get_buttons())
        except MessageNotModified:
            pass

    elif query.data.lower() == "seek":
        if not Config.CALL_STATUS:
            return await query.answer("⛔️ Empty Playlist !", show_alert=True)
        if not (Config.playlist or Config.STREAM_LINK):
            return await query.answer("⚠️ Startup Stream Can't Be Seeked !", show_alert=True)
        data=Config.DATA.get('FILE_DATA')
        if not data.get('dur', 0) or \
            data.get('dur') == 0:
            return await query.answer("⚠️ This Stream Can't Be Seeked !", show_alert=True)
        k, reply = await seek_file(10)
        if k == False:
            return await query.answer(reply, show_alert=True)
        try:
            await query.message.edit_reply_markup(reply_markup=await get_buttons())
        except MessageNotModified:
            pass

    elif query.data.lower() == "rewind":
        if not Config.CALL_STATUS:
            return await query.answer("⛔️ Empty Playlist !", show_alert=True)
        if not (Config.playlist or Config.STREAM_LINK):
            return await query.answer("⚠️ Startup Stream Can't Be Seeked !", show_alert=True)
        data=Config.DATA.get('FILE_DATA')
        if not data.get('dur', 0) or \
            data.get('dur') == 0:
            return await query.answer("⚠️ This Stream Can't Be Seeked !", show_alert=True)
        k, reply = await seek_file(-10)
        if k == False:
            return await query.answer(reply, show_alert=True)
        try:
            await query.message.edit_reply_markup(reply_markup=await get_buttons())
        except MessageNotModified:
            pass

    elif query.data.lower() == "usage":
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
        try:
            await query.message.edit(
                HELP_TEXT,
                reply_markup=reply_markup
            )
        except MessageNotModified:
            pass

    elif query.data.lower() == "home":
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
        try:
            await query.message.edit(
                HOME_TEXT.format(query.from_user.first_name, query.from_user.id),
                reply_markup=reply_markup
            )
        except MessageNotModified:
            pass

    elif query.data.lower() == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            pass

    await query.answer()

