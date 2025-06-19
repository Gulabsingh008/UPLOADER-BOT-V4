import requests
import asyncio
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.enums import ParseMode


def detect_platform(url):
    if "instagram.com" in url:
        return "instagram"
    elif "pinterest.com" in url:
        return "pinterest"
    elif "twitter.com" in url or "x.com" in url:
        return "twitter"
    elif url.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return "image"
    else:
        return "yt-dlp"


def get_instagram_media(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for meta in soup.find_all("meta"):
            if meta.get("property") == "og:video":
                return meta.get("content")
            elif meta.get("property") == "og:image":
                return meta.get("content")
    except:
        return None


def get_pinterest_media(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        tag = soup.find("meta", {"property": "og:image"})
        return tag.get("content") if tag else None
    except:
        return None


def get_twitter_media(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        meta = soup.find("meta", {"property": "og:video"}) or soup.find("meta", {"property": "og:image"})
        return meta.get("content") if meta else None
    except:
        return None


async def get_yt_dlp_download(url):
    try:
        command = ["yt-dlp", "-g", url]
        process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE)
        stdout, _ = await process.communicate()
        return stdout.decode().split("\n")[0] if stdout else None
    except:
        return None


async def universal_downloader(bot, message, url):
    await message.reply("🔍 Detecting link...", quote=True)
    platform = detect_platform(url)

    if platform == "instagram":
        media_url = get_instagram_media(url)
    elif platform == "pinterest":
        media_url = get_pinterest_media(url)
    elif platform == "twitter":
        media_url = get_twitter_media(url)
    elif platform == "image":
        media_url = url
    else:
        media_url = await get_yt_dlp_download(url)

    if media_url:
        await message.reply_document(document=media_url, caption="✅ Here's your media")
    else:
        await message.reply("❌ Unable to download media from this link.")


@Client.on_message(filters.command("get") & filters.private)
async def get_any_link(bot, message):
    if len(message.command) < 2:
        return await message.reply("🔗 Usage: `/get <link>`", parse_mode=ParseMode.MARKDOWN)

    url = message.command[1]
    await universal_downloader(bot, message, url)
