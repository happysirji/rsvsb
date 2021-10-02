from config import Config
from logger import LOGGER
from pyrogram import Client, errors
from youtubesearchpython import VideosSearch
from pyrogram.handlers import InlineQueryHandler
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup

buttons = [
            [
                InlineKeyboardButton("❔ HOW TO USE ME ❔", callback_data="help"),
            ],
            [
                InlineKeyboardButton("CHANNEL", url="https://t.me/rsbro"),
                InlineKeyboardButton("GROUP", url="https://t.me/joinchat/_8Tt7Srw5MQ4YTNl"),
            ]
         ]

def get_cmd(dur):
    if dur:
        return "/pl"
    else:
        return "/stream"

@Client.on_inline_query()
async def search(client, query):
    answers = []
    if query.query == "DJ RS":
        answers.append(
            InlineQueryResultArticle(
                title="RS Video Player Bot",
                input_message_content=InputTextMessageContent(f"{Config.REPLY_MESSAGE}\n\n<b>© Powered By : \n@rsbro</b>", disable_web_page_preview=True),
                reply_markup=InlineKeyboardMarkup(buttons)
                )
            )
        await query.answer(results=answers, cache_time=0)
        return
    string = query.query.lower().strip().rstrip()
    if string == "":
        await client.answer_inline_query(
            query.id,
            results=answers,
            switch_pm_text=("✍️ Type A Video Name !"),
            switch_pm_parameter="usage",
            cache_time=0
        )
    else:
        videosSearch = VideosSearch(string.lower(), limit=50)
        for v in videosSearch.result()["result"]:
            answers.append(
                InlineQueryResultArticle(
                    title=v["title"],
                    description=("Duration: {} Views: {}").format(
                        v["duration"],
                        v["viewCount"]["short"]
                    ),
                    input_message_content=InputTextMessageContent(
                        "{} https://www.youtube.com/watch?v={}".format(get_cmd(v["duration"]), v["id"])
                    ),
                    thumb_url=v["thumbnails"][0]["url"]
                )
            )
        try:
            await query.answer(
                results=answers,
                cache_time=0
            )
        except errors.QueryIdInvalid:
            await query.answer(
                results=answers,
                cache_time=0,
                switch_pm_text=("❌ No Results Found !"),
                switch_pm_parameter="",
            )


__handlers__ = [
    [
        InlineQueryHandler(
            search
        )
    ]
]
