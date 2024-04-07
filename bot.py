import os
import time
import math
import shutil
import asyncio
import random
import shlex
from urllib.parse import unquote
from urllib.error import HTTPError
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from pyrogram.errors import BadRequest
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from typing import Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configs
API_HASH = os.environ.get('API_HASH') # Api hash
APP_ID = int(os.environ.get('APP_ID')) # Api id/App id
BOT_TOKEN = os.environ.get('BOT_TOKEN') # Bot token
OWNER_ID = os.environ.get('OWNER_ID') # Your telegram id
AS_ZIP = bool(os.environ.get('AS_ZIP', False)) # Upload method. If True: will Zip all your files and send as zipfile | If False: will send file one by one
BUTTONS = bool(os.environ.get('BUTTONS', False)) # Upload mode. If True: will send buttons (Zip or One by One) instead of AZ_ZIP | If False: will do as you've fill on AZ_ZIP

# Modify the start message handler to include information about the new features
@xbot.on_message(filters.command('start') & OWNER_FILTER & filters.private)
async def start(bot, update):
    await update.reply_text(f"I'm BulkLoader\nYou can upload list of urls\n\nTo bulk download, use /link command and then send URLs or a text file containing URLs.\nTo rename files, use /rename command.", True, reply_markup=InlineKeyboardMarkup(START_BUTTONS))

# Add a new command to handle bulk downloads
@xbot.on_message(filters.command('link') & OWNER_FILTER & filters.private)
async def linkloader(bot, update):
    xlink = await update.chat.ask('Send your links, separated each link by new line or upload a text file containing URLs', filters=filters.text | filters.document, timeout=300)
    urls = []
    if xlink.text:
        urls = xlink.text.split('\n')
    elif xlink.document:
        file_path = await xlink.download()
        with open(file_path, 'r') as file:
            urls = file.readlines()
    # Download and send the files
    await download_and_send_files(urls, update)

# Function to download and send files
async def download_and_send_files(urls, update):
    # Download files
    downloaded_files = []
    for url in urls:
        # Download the file
        # Add logic to download the file based on the URL
        downloaded_files.append(downloaded_file_path)
    
    # Rename files
    renamed_files = []
    for file in downloaded_files:
        # Rename the file
        # Add logic to rename the file based on user input
        renamed_files.append(renamed_file_path)
    
    # Send renamed files
    for file in renamed_files:
        # Send the file
        # Add logic to send the file to the user

# Add a new command to handle file renaming
@xbot.on_message(filters.command('rename') & OWNER_FILTER & filters.private)
async def rename_files(bot, update):
    # Ask the user for the new names
    await update.reply_text("Please enter new names for the files, separated by new lines.")
    new_names = await update.chat.get_reply()

    # Rename the files
    renamed_files = []
    for file in downloaded_files:
        # Rename the file
        # Add logic to rename the file based on the new names provided by the user
        renamed_files.append(renamed_file_path)
    
    # Send renamed files
    for file in renamed_files:
        # Send the file
        # Add logic to send the file to the user

# Buttons
START_BUTTONS=[
    [
        InlineKeyboardButton("Source", url="https://github.com/X-Gorn/BulkLoader"),
        InlineKeyboardButton("LinkTree", url="https://xgorn.is-a.dev"),
    ],
    [InlineKeyboardButton("Author", url="https://t.me/xgorn")],
]

CB_BUTTONS=[
    [
        InlineKeyboardButton("Zip", callback_data="zip"),
        InlineKeyboardButton("One by one", callback_data="1by1"),
    ]
]

# Helpers

# https://github.com/SpEcHiDe/AnyDLBot
async def progress_for_pyrogram(
    current,
    total,
    ud_type,
    message,
    start
):
    now = time.time()
    diff = now - start
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
            estimated_total_time if estimated_total_time != '' else "0 s"
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
    power = 2**10
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

async def send_media(file_name: str, update: Message) -> bool:
    if os.path.isfile(file_name):
        files = file_name
        pablo = update
        if not os.path.isfile(files):
            caption = files
        else:
            caption = files.split('/')[-1]
        progress_args = ('Uploading...', pablo, time.time())
        if files.lower().endswith(('.mkv', '.mp4')):
            metadata = extractMetadata(createParser(files))
            duration = 0
            if metadata is not None:
                if metadata.has("duration"):
                    duration = metadata.get('duration').seconds
            rndmtime = str(random.randint(0, duration))
            await run_cmd(f'ffmpeg -ss {rndmtime} -i "{files}" -vframes 1 thumbnail.jpg')
            await update.reply_video(files, caption=caption, duration=duration, thumb='thumbnail.jpg', progress=progress_for_pyrogram, progress_args=progress_args)
            os.remove('thumbnail.jpg')
        elif files.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                await update.reply
                
