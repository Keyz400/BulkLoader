import asyncio
import math
import os
import random
import shlex
import shutil
import time
from typing import Tuple

from dotenv import load_dotenv
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import BadRequest
from urllib.error import HTTPError

# Load environment variables from .env file
load_dotenv()

# Configs
API_HASH = os.environ.get('API_HASH')
APP_ID = int(os.environ.get('APP_ID'))
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OWNER_ID = os.environ.get('OWNER_ID')
AS_ZIP = bool(os.environ.get('AS_ZIP', False))
BUTTONS = bool(os.environ.get('BUTTONS', False))

# Constants
START_BUTTONS = [
    [
        InlineKeyboardButton("Source", url="https://github.com/X-Gorn/BulkLoader"),
        InlineKeyboardButton("LinkTree", url="https://xgorn.is-a.dev"),
    ],
    [InlineKeyboardButton("Author", url="https://t.me/xgorn")],
]

CB_BUTTONS = [
    [
        InlineKeyboardButton("Zip", callback_data="zip"),
        InlineKeyboardButton("One by one", callback_data="1by1"),
    ]
]


# Helper functions
async def progress_for_pyrogram(
    current,
    total,
    ud_type,
    message,
    start
):
    now = time.time()
    diff = now - start
    if diff == 0:
        return
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "[{0}{1}] \nP: {2}%\n".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))

        tmp = progress + "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time if estimated_total_time else "0 s"
        )
        try:
            await message.edit(
                text="{}\n {}".format(
                    ud_type,
                    tmp
                )
            )
        except:
            pass


def humanbytes(size):
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s, ") if seconds else "") + \
          ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]


async def run_cmd(cmd) -> Tuple[str, str, int, int]:
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


# Rest of the code remains the same
