# ©️ LISA-KOREA | @LISA_FAN_LK | NT_BOT_CHANNEL | TG-SORRY

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import requests, urllib.parse, filetype, os, time, shutil, tldextract, asyncio, json, math, instaloader
from bs4 import BeautifulSoup
from PIL import Image
from plugins.config import Config
from plugins.script import Translation
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import filters
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

# Initialize Instaloader
L = instaloader.Instaloader(
    dirname_pattern='downloads/instaloader',
    save_metadata=False,
    download_videos=True,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    compress_json=False
)

# Load cookies if available
if os.path.exists('cookies.txt'):
    try:
        L.load_session_from_file('instagram', 'cookies.txt')
        logger.info("Instagram cookies loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Instagram cookies: {e}")

def detect_platform(url):
    if "instagram.com" in url:
        return "instagram"
    elif "pinterest.com" in url:
        return "pinterest"
    elif "twitter.com" in url or "x.com" in url:
        return "twitter"
    elif "snapchat.com" in url:
        return "snapchat"
    elif url.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return "image"
    else:
        return "yt-dlp"

async def download_instagram_media(url):
    try:
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Create user specific directory
        download_dir = f"downloads/instaloader/{post.owner_username}_{shortcode}"
        os.makedirs(download_dir, exist_ok=True)
        
        # Download the post
        L.download_post(post, target=download_dir)
        
        # Find the downloaded file
        for file in os.listdir(download_dir):
            if file.endswith(('.mp4', '.jpg', '.jpeg', '.png')):
                return os.path.join(download_dir, file)
        return None
    except Exception as e:
        logger.error(f"Instaloader error: {e}")
        return None

async def get_direct_media(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        meta = soup.find("meta", {"property": "og:video"}) or soup.find("meta", {"property": "og:image"})
        return meta.get("content") if meta else None
    except Exception as e:
        logger.error(f"Direct media fetch error: {e}")
        return None

async def handle_yt_dlp_download(bot, update, url):
    youtube_dl_username = None
    youtube_dl_password = None
    file_name = None

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

    if Config.HTTP_PROXY != "":
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--allow-dynamic-mpd",
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

    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    
    if e_response and "nonnumeric port" not in e_response:
        error_message = e_response.replace("please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output.", "")
        if "This video is only available for registered users." in error_message:
            error_message += Translation.SET_CUSTOM_USERNAME_PASSWORD
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
                else:
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
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION.format(Thumbnail) + "\n" + Translation.SET_CUSTOM_USERNAME_PASSWORD,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            reply_to_message_id=update.id
        )

@Client.on_message(filters.private & filters.regex(pattern=".*http.*"))
async def smart_downloader(bot, update):
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

    url = update.text.strip()
    platform = detect_platform(url)
    
    # Processing message
    chk = await bot.send_message(
        chat_id=update.chat.id,
        text=f'ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʟɪɴᴋ ⌛',
        disable_web_page_preview=True,
        reply_to_message_id=update.id,
        parse_mode=enums.ParseMode.HTML
    )
    
    try:
        # Instagram specific handling
        if platform == "instagram":
            # Try instaloader first
            file_path = await download_instagram_media(url)
            if file_path:
                if file_path.endswith('.mp4'):
                    await update.reply_video(
                        video=file_path,
                        caption="✅ Downloaded via Instaloader",
                        reply_to_message_id=update.id
                    )
                else:
                    await update.reply_photo(
                        photo=file_path,
                        caption="✅ Downloaded via Instaloader",
                        reply_to_message_id=update.id
                    )
                # Clean up
                shutil.rmtree(os.path.dirname(file_path))
                await chk.delete()
                return
                
            # Fallback to direct method
            media_url = await get_direct_media(url)
            if media_url:
                if media_url.endswith('.mp4'):
                    await update.reply_video(
                        video=media_url,
                        caption="✅ Downloaded via Direct Link",
                        reply_to_message_id=update.id
                    )
                else:
                    await update.reply_photo(
                        photo=media_url,
                        caption="✅ Downloaded via Direct Link",
                        reply_to_message_id=update.id
                    )
                await chk.delete()
                return
                
            # Final fallback to yt-dlp
            await handle_yt_dlp_download(bot, update, url)
            await chk.delete()
            return
            
        # Other platforms
        elif platform in ["pinterest", "twitter", "snapchat"]:
            media_url = await get_direct_media(url)
            if media_url:
                if media_url.endswith('.mp4'):
                    await update.reply_video(media_url)
                else:
                    await update.reply_photo(media_url)
                await chk.delete()
                return
                
        # Direct images
        elif platform == "image":
            await update.reply_photo(url)
            await chk.delete()
            return
            
        # Default yt-dlp handler
        await handle_yt_dlp_download(bot, update, url)
        await chk.delete()
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        await chk.edit_text(f"⚠️ Error: {str(e)}")
        if "login_required" in str(e):
            await update.reply_text(
                "🔒 Instagram requires login. Please send cookies.txt file",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("How to Get Cookies", url="https://example.com/cookies-guide")]
                ])
            )
