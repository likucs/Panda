#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MIT License
# Copyright (c) 2020 Stɑrry Shivɑm // This file is part of AcuteBot
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import speedtest
import requests as r
import subprocess
import random

from pythonping import ping as pingger
from acutebot.helpers.database import users_sql as sql
from acutebot.helpers.database.favorites_sql import fav_count
import acutebot.helpers.strings as st
from acutebot import dp, typing, DEV_ID, LOG

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext.dispatcher import run_async
from telegram.ext import CommandHandler, MessageHandler, Filters


@run_async
@typing
def get_ip(update, context):
    res = r.get("http://ipinfo.io/ip")
    update.message.reply_text(res.text)


@run_async
@typing
def ping(update, context):
    tg_api = pingger("api.telegram.org", count=4)
    text = "*Pong!*\n"
    text += (
        f"Average speed to Telegram bot API server - <pre>{tg_api.rtt_avg_ms}</pre> ms"
    )
    update.effective_message.reply_text(text)


# Taken from PaperPlane Extended userbot
def speed_convert(size):
    """
    Hi human, you can't read bytes?
    """
    power = 2 ** 10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "Mb/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


@run_async
@typing
def speed(update, context):
    message = update.effective_message
    ed_msg = message.reply_text("<pre>Running speed test . . .</pre>")
    test = speedtest.Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    context.bot.editMessageText(
        "Download: "
        f"<pre>{speed_convert(result['download'])}</pre> \n"
        "Upload: "
        f"<pre>{speed_convert(result['upload'])}</pre> \n"
        "Ping: "
        f"<pre>{result['ping']}</pre> \n"
        "ISP: "
        f"<pre>{result['client']['isp']}</pre>",
        update.effective_chat.id,
        ed_msg.message_id,
    )


@run_async
def rmemes(update, context):
    msg = update.effective_message
    chat = update.effective_chat

    SUBREDS = [
        "meirl",
        "dankmemes",
        "AdviceAnimals",
        "memes",
        "meme",
        "memes_of_the_dank",
        "PornhubComments",
        "teenagers",
        "memesIRL",
        "insanepeoplefacebook",
        "terriblefacebookmemes",
    ]

    subreddit = random.choice(SUBREDS)
    res = r.get(f"https://meme-api.herokuapp.com/gimme/{subreddit}")

    if res.status_code != 200:  # Like if api is down?
        return msg.reply_text(st.API_ERR)
    else:
        res = res.json()

    keyb = [[InlineKeyboardButton(text=f"r/{res['subreddit']}", url=res["postLink"])]]
    try:
        context.bot.send_chat_action(chat.id, "upload_photo")
        context.bot.send_photo(
            chat.id,
            photo=res["url"],
            caption=(res["title"]),
            reply_markup=InlineKeyboardMarkup(keyb),
            timeout=60,
        )

    except BadRequest as excp:
        LOG.error(excp)


@run_async
def stats(update, context):
    msg = update.effective_message
    return msg.reply_text(
        st.STATS.format(sql.users_count(), sql.chats_count(), fav_count()),
        parse_mode=None,
    )


@run_async
def greet(update, context):
    msg = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    new_members = msg.new_chat_members
    for new_mem in new_members:
        if new_mem.id == context.bot.id:
            msg.reply_text(
                st.GREET.format(user.first_name, chat.title))

@run_async
@typing
def neofetch(update, context):
    msg = update.effective_message
    try:
        res = subprocess.Popen(
            ["neofetch", "--stdout",], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        stdout, stderr = res.communicate()
        result = str(stdout.decode().strip()) + str(stderr.decode().strip())
        msg.reply_text("<code>" + result + "</code>")
    except FileNotFoundError:
        msg.reply_text("Install neofetch!")


IP_HANDLER = CommandHandler("ip", get_ip, filters=Filters.chat(DEV_ID))
PING_HANDLER = CommandHandler("ping", ping, filters=Filters.user(DEV_ID))
SPEEDTEST_HANDLER = CommandHandler("speedtest", speed, filters=Filters.user(DEV_ID))
REDDIT_HANDLER = CommandHandler("reddit", rmemes)
STATS_HANDLER = CommandHandler("stats", stats, filters=Filters.user(DEV_ID))
NEOFETCH_HANDLER = CommandHandler("neofetch", neofetch, filters=Filters.user(DEV_ID))
GREET_HANDLER = MessageHandler(Filters.status_update.new_chat_members, greet)

dp.add_handler(IP_HANDLER)
dp.add_handler(PING_HANDLER)
dp.add_handler(SPEEDTEST_HANDLER)
dp.add_handler(REDDIT_HANDLER)
dp.add_handler(STATS_HANDLER)
dp.add_handler(NEOFETCH_HANDLER)
dp.add_handler(GREET_HANDLER)
