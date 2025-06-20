# ©️ LISA-KOREA | @LISA_FAN_LK | NT_BOT_CHANNEL | TG-SORRY

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import requests, urllib.parse, filetype, os, time, shutil, tldextract, asyncio, json, math, re
from PIL import Image
from plugins.config import Config
from plugins.script import Translation
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import filters
from pyrogram.types import Message
import os
import time
import random
from pyrogram import enums
from pyrogram import Client
from plugins.functions.verify import verify_user, check_token, check_verification, get_token
from plugins.functions.forcesub import handle_force_subscribe
from plugins.functions.display_progress import humanbytes
from plugins.functions.help_uploadbot import DownLoadFile
from plugins.functions.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from plugins.functions.ran_text import random_char
from plugins.database.database import db
from plugins.database.add import AddUser
from pyrogram.types import Thumbnail
from bs4 import BeautifulSoup

cookies_file = 'cookies.txt'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.google.com/"
}


import logging
import os
import re
import shutil
import time
import requests
from bs4 import BeautifulSoup
from PIL import Image
from filetype import is_image, is_video
from pyrogram import Client, filters
from pyrogram.types import Message

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== Improved Media Downloader ==========
async def download_media(url: str, user_id: int) -> str:
    """Enhanced universal downloader with format handling"""
    try:
        # Create temp directory
        temp_dir = f"downloads/{user_id}"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate safe filename
        filename = re.sub(r'[^\w\-_. ]', '_', url.split('/')[-1].split('?')[0])
        if not any(filename.lower().endswith(ext) for ext in ['.jpg','.jpeg','.png','.mp4','.webp']):
            filename += '.jpg'
            
        filepath = f"{temp_dir}/{filename}"
        
        # Download with Instagram-style headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Accept': 'image/webp,image/*,*/*;q=0.8'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=20)
        response.raise_for_status()
        
        # Download with progress tracking
        downloaded = 0
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
                downloaded += len(chunk)
                
        # Verify download completed
        if downloaded < 1024:  # Less than 1KB indicates failure
            raise ValueError("Incomplete download")
            
        # Convert WebP to JPEG if needed
        if filepath.endswith('.webp'):
            jpg_path = filepath.replace('.webp', '.jpg')
            try:
                with Image.open(filepath) as img:
                    img.convert('RGB').save(jpg_path, 'JPEG', quality=95)
                os.remove(filepath)
                filepath = jpg_path
            except Exception as conv_error:
                logger.error(f"WebP conversion failed: {conv_error}")
                os.remove(filepath)
                return None
                
        return filepath
        
    except Exception as e:
        logger.error(f"Media download error: {e}")
        return None

# ========== Enhanced Social Media Extractors ==========
def extract_twitter_media(url):
    """Improved Twitter media extractor"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try for video
        video = soup.find('meta', {'property': 'og:video'}) or \
                soup.find('meta', {'name': 'twitter:player:stream'})
        if video:
            return video.get('content')
        
        # Try for image
        image = soup.find('meta', {'property': 'og:image'}) or \
                soup.find('meta', {'name': 'twitter:image'})
        if image:
            return image.get('content')
            
        return None
    except Exception as e:
        logger.error(f"Twitter extractor error: {e}")
        return None

def extract_pinterest_media(url):
    """Improved Pinterest media extractor"""
    try:
        headers = {
            'User-Agent': 'Pinterest/3.0 (iPhone; iOS 15_0; Scale/3.00)'
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        image = soup.find('meta', {'property': 'og:image'}) or \
                soup.find('meta', {'name': 'pinterest:image'])
        return image.get('content') if image else None
    except Exception as e:
        logger.error(f"Pinterest extractor error: {e}")
        return None

def extract_instagram_media(url):
    """Improved Instagram media extractor"""
    try:
        headers = {
            'User-Agent': 'Instagram 219.0.0.12.117 Android',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try video first
        video = soup.find('meta', {'property': 'og:video'})
        if video:
            return video.get('content')
        
        # Then image
        image = soup.find('meta', {'property': 'og:image'})
        if image:
            return image.get('content')
            
        return None
    except Exception as e:
        logger.error(f"Instagram extractor error: {e}")
        return None

# ========== Command Handlers ==========
@Client.on_message(filters.command(["dwnld", "download"]) & filters.regex(r'https?://[^\s]+'))
async def media_download_handler(bot: Client, message: Message):
    """Enhanced media download handler"""
    try:
        url = message.text.split(' ', 1)[1].strip()
        processing_msg = await message.reply("🔍 Processing your link...", quote=True)
        
        # Platform detection
        if "instagram.com" in url:
            media_url = extract_instagram_media(url)
        elif "twitter.com" in url or "x.com" in url:
            media_url = extract_twitter_media(url)
        elif "pinterest.com" in url:
            media_url = extract_pinterest_media(url)
        else:
            media_url = url  # Try direct download
            
        # Download the media
        filepath = await download_media(media_url or url, message.from_user.id)
        
        if not filepath:
            await processing_msg.edit_text("❌ Couldn't download media (invalid or unsupported)")
            return
            
        # Verify file exists and has content
        if not os.path.exists(filepath) or os.path.getsize(filepath) < 1024:
            await processing_msg.edit_text("❌ Downloaded file is corrupted")
            return
            
        # Send appropriate media type
        try:
            if is_image(filepath):
                await message.reply_chat_action("upload_photo")
                await message.reply_photo(filepath)
            elif is_video(filepath):
                await message.reply_chat_action("upload_video")
                await message.reply_video(filepath)
            else:
                await message.reply_document(filepath)
        except Exception as send_error:
            logger.error(f"Media sending error: {send_error}")
            await processing_msg.edit_text("❌ Failed to send media (format may be unsupported)")
            return
            
        # Clean up
        try:
            os.remove(filepath)
            await processing_msg.delete()
        except Exception as clean_error:
            logger.error(f"Cleanup error: {clean_error}")
            
    except IndexError:
        await message.reply_text("Please provide a URL after /dwnld command\nExample: /dwnld https://example.com/image.jpg")
    except Exception as e:
        logger.error(f"Handler error: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")
# ============= KEEP YOUR ORIGINAL CODE COMPLETELY UNCHANGED BELOW =============
@Client.on_message(filters.private & filters.regex(pattern=".*http.*"))
async def echo(bot, update):
    if update.from_user.id != Config.OWNER_ID:  
        if not await check_verification(bot, update.from_user.id) and Config.TRUE_OR_FALSE:
            button = [[
                InlineKeyboardButton("✓⃝ Vᴇʀɪꜰʏ ✓⃝", url=await get_token(bot, update.from_user.id, f"https://telegram.me/{Config.BOT_USERNAME}?start="))
                ],[
                InlineKeyboardButton("🔆 Wᴀᴛᴄʜ Hᴏᴡ Tᴏ Vᴇʀɪꜰʏ 🔆", url=f"{Config.VERIFICATION}")
            ]]
            await update.reply_text(
                text="<b>Pʟᴇᴀsᴇ Vᴇʀɪꜰʏ Fɪʀsᴛ Tᴏ Usᴇ Mᴇ</b>",
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(button)
            )
            return
            
    if Config.LOG_CHANNEL:
        try:
            log_message = await update.forward(Config.LOG_CHANNEL)
            log_info = "Message Sender Information\n"
            log_info += "\nFirst Name: " + update.from_user.first_name
            log_info += "\nUser ID: " + str(update.from_user.id)
            log_info += "\nUsername: @" + (update.from_user.username if update.from_user.username else "")
            log_info += "\nUser Link: " + update.from_user.mention
            await log_message.reply_text(
                text=log_info,
                disable_web_page_preview=True,
                quote=True
            )
        except Exception as error:
            print(error)
            
    if not update.from_user:
        return await update.reply_text("I don't know about you sar :(")
        
    await AddUser(bot, update)
    
    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, update)
        if fsub == 400:
            return

    logger.info(update.from_user)
    url = update.text
    youtube_dl_username = None
    youtube_dl_password = None
    file_name = None

    print(url)
    if "|" in url:
        url_parts = url.split("|")
        if len(url_parts) == 2:
            url = url_parts[0]
            file_name = url_parts[1]
        elif len(url_parts) == 4:
            url = url_parts[0]
            file_name = url_parts[1]
            youtube_dl_username = url_parts[2]
            youtube_dl_password = url_parts[3]
        else:
            for entity in update.entities:
                if entity.type == "text_link":
                    url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    url = url[o:o + l]
        if url is not None:
            url = url.strip()
        if file_name is not None:
            file_name = file_name.strip()
        if youtube_dl_username is not None:
            youtube_dl_username = youtube_dl_username.strip()
        if youtube_dl_password is not None:
            youtube_dl_password = youtube_dl_password.strip()
        logger.info(url)
        logger.info(file_name)
    else:
        for entity in update.entities:
            if entity.type == "text_link":
                url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                url = url[o:o + l]
    if Config.HTTP_PROXY != "":
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--allow-dynamic-mpd",
            "--cookies", cookies_file,
            "--no-check-certificate",
            "-j",
            url,
            "--proxy", Config.HTTP_PROXY
        ]
    else:
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--allow-dynamic-mpd",
            "--cookies", cookies_file,
            "--no-check-certificate",
            "-j",
            url,
            "--geo-bypass-country",
            "IN"

        ]
    if youtube_dl_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(youtube_dl_username)
    if youtube_dl_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(youtube_dl_password)
    logger.info(command_to_exec)
    chk = await bot.send_message(
            chat_id=update.chat.id,
            text=f'ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʟɪɴᴋ ⌛',
            disable_web_page_preview=True,
            reply_to_message_id=update.id,
            parse_mode=enums.ParseMode.HTML
          )
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    logger.info(e_response)
    t_response = stdout.decode().strip()
    if e_response and "nonnumeric port" not in e_response:
        # logger.warn("Status : FAIL", exc.returncode, exc.output)
        error_message = e_response.replace("please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output.", "")
        if "This video is only available for registered users." in error_message:
            error_message += Translation.SET_CUSTOM_USERNAME_PASSWORD
        await chk.delete()
        
        time.sleep(10)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NO_VOID_FORMAT_FOUND.format(str(error_message)),
            reply_to_message_id=update.id,
            disable_web_page_preview=True
        )
        return False
    if t_response:
        x_reponse = t_response
        if "\n" in x_reponse:
            x_reponse, _ = x_reponse.split("\n")
        response_json = json.loads(x_reponse)
        randem = random_char(5)
        save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + f'{randem}' + ".json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)
        # logger.info(response_json)
        inline_keyboard = []
        duration = None
        if "duration" in response_json:
            duration = response_json["duration"]
        if "formats" in response_json:
            for formats in response_json["formats"]:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note")
                if format_string is None:
                    format_string = formats.get("format")
                if "DASH" in format_string.upper():
                    continue
          
                format_ext = formats.get("ext")
                if formats.get('filesize'):
                    size = formats['filesize']
                elif formats.get('filesize_approx'):
                    size = formats['filesize_approx']
                else:
                    size = 0
                cb_string_video = "{}|{}|{}|{}".format(
                    "video", format_id, format_ext, randem)
                cb_string_file = "{}|{}|{}|{}".format(
                    "file", format_id, format_ext, randem)
                if format_string is not None and not "audio only" in format_string:
                    ikeyboard = [
                        InlineKeyboardButton(
                            "📁 " + format_string + " " + format_ext + " " + humanbytes(size) + " ",
                            callback_data=(cb_string_video).encode("UTF-8")
                        )
                    ]
                    """if duration is not None:
                        cb_string_video_message = "{}|{}|{}|{}|{}".format(
                            "vm", format_id, format_ext, ran, randem)
                        ikeyboard.append(
                            InlineKeyboardButton(
                                "VM",
                                callback_data=(
                                    cb_string_video_message).encode("UTF-8")
                            )
                        )"""
                else:
                    # special weird case :\
                    ikeyboard = [
                        InlineKeyboardButton(
                            "📁 [" +
                            "] ( " +
                            humanbytes(size) + " )",
                            callback_data=(cb_string_video).encode("UTF-8")
                        )
                    ]
                inline_keyboard.append(ikeyboard)
            if duration is not None:
                cb_string_64 = "{}|{}|{}|{}".format("audio", "64k", "mp3", randem)
                cb_string_128 = "{}|{}|{}|{}".format("audio", "128k", "mp3", randem)
                cb_string_320 = "{}|{}|{}|{}".format("audio", "320k", "mp3", randem)
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "🎵 ᴍᴘ𝟹 " + "(" + "64 ᴋʙᴘs" + ")", callback_data=cb_string_64.encode("UTF-8")),
                    InlineKeyboardButton(
                        "🎵 ᴍᴘ𝟹 " + "(" + "128 ᴋʙᴘs" + ")", callback_data=cb_string_128.encode("UTF-8"))
                ])
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "🎵 ᴍᴘ𝟹 " + "(" + "320 ᴋʙᴘs" + ")", callback_data=cb_string_320.encode("UTF-8"))
                ])
                inline_keyboard.append([                 
                    InlineKeyboardButton(
                        "🔒 ᴄʟᴏsᴇ", callback_data='close')               
                ])
        else:
            format_id = response_json["format_id"]
            format_ext = response_json["ext"]
            cb_string_file = "{}|{}|{}|{}".format(
                "file", format_id, format_ext, randem)
            cb_string_video = "{}|{}|{}|{}".format(
                "video", format_id, format_ext, randem)
            inline_keyboard.append([
                InlineKeyboardButton(
                    "📁 Document",
                    callback_data=(cb_string_video).encode("UTF-8")
                )
            ])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await chk.delete()
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION.format(Thumbnail) + "\n" + Translation.SET_CUSTOM_USERNAME_PASSWORD,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            reply_to_message_id=update.id
        )
    else:
        #fallback for nonnumeric port a.k.a seedbox.io
        inline_keyboard = []
        cb_string_file = "{}={}={}".format(
            "file", "LFO", "NONE")
        cb_string_video = "{}={}={}".format(
            "video", "OFL", "ENON")
        inline_keyboard.append([
            InlineKeyboardButton(
                "📁 ᴍᴇᴅɪᴀ",
                callback_data=(cb_string_video).encode("UTF-8")
            )
        ])
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await chk.delete(True)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            reply_to_message_id=update.id
        )
