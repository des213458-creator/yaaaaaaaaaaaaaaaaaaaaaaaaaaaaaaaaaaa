#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, asyncio, tempfile, shutil, logging
from pathlib import Path
from urllib.parse import urlparse

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Set BOT_TOKEN environment variable")

# N is required (we will try to download it during build). This bot assumes N_m3u8DL-RE exists and is executable.
N_BIN = Path.cwd() / "N_m3u8DL-RE"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

def safe_filename_from_url(url: str):
    parsed = urlparse(url)
    name = os.path.basename(parsed.path) or "output"
    name = "".join(c for c in name if c.isalnum() or c in "._-") or "output"
    if not name.lower().endswith(".mp4"):
        name += ".mp4"
    return name

async def run_subprocess(cmd, cwd=None, timeout=None):
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd)
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return -1, b"", b"timeout"
    return proc.returncode, stdout, stderr

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.reply("مرحبًا! أرسل رابط .m3u8 أو استخدم /download <الرابط> وسأقوم بتنزيله وإرساله لك.")


@dp.message_handler(commands=["download"])
async def cmd_download(message: types.Message):
    args = message.get_args().strip()
    if not args:
        await message.reply("أرسل: /download <رابط_m3u8>")
        return
    await handle_m3u8_url(message, args)


@dp.message_handler()
async def text_message(message: types.Message):
    text = (message.text or "").strip()
    if text.lower().endswith('.m3u8') or '.m3u8' in text:
        for tok in text.split():
            if tok.startswith('http') and '.m3u8' in tok:
                await handle_m3u8_url(message, tok)
                return
    # ignore other messages


async def handle_m3u8_url(message: types.Message, url: str):
    chat_id = message.chat.id
    status = await message.reply(f"جاري التحقق وبدء التنزيل: {url}")

    tmpdir = Path(tempfile.mkdtemp(prefix="m3u8dl_"))
    out_name = safe_filename_from_url(url)
    try:
        # Ensure N exists
        if not N_BIN.exists():
            await status.edit_text("خطأ: أداة N_m3u8DL-RE غير متوفرة على الخادم. يرجى التحقق من الإعدادات.")
            return

        await status.edit_text("جاري التنزيل باستخدام N_m3u8DL-RE — الرجاء الانتظار...")
        # Call N to download into tmpdir and save with base name
        cmd = [str(N_BIN), url, '--save-name', out_name.rsplit('.',1)[0], '--save-dir', str(tmpdir), '--no-log']
        rc, out, err = await run_subprocess(cmd, timeout=1800)  # 30 minutes timeout
        if rc != 0:
            await status.edit_text(f"N_m3u8DL-RE فشل أثناء التنزيل.")
موجز الخطأ:
{err.decode(errors='ignore')[:1000]}")
            return

        # find produced file
        candidates = list(tmpdir.glob('**/*'))
        mp = None
        for c in candidates:
            if c.is_file() and c.suffix.lower() in ['.mp4', '.mkv', '.ts', '.mov', '.m4a']:
                mp = c
                break
        if mp is None:
            await status.edit_text("لم أجد ملف مخرجات بعد تشغيل N. تحقق من لوغ N.")
            return

        size_mb = mp.stat().st_size / (1024*1024)
        await status.edit_text(f"اكتمل التنزيل. الحجم: {size_mb:.1f} MB — جارٍ الإرسال إلى Telegram...")

        try:
            with mp.open('rb') as f:
                await bot.send_document(chat_id, (mp.name, f))
            await status.delete()
        except Exception as e:
            await status.edit_text(f"تم إنشاء الملف لكن حدث خطأ عند رفعه لتليجرام: {e}
قد تحتاج رفعه لمخدم خارجي إذا كان كبيرًا جدًا.")

    finally:
        # cleanup tmpdir
        try:
            for p in tmpdir.glob('**/*'):
                if p.is_file():
                    p.unlink()
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
