import asyncio
import logging
import os
import tempfile

from aiogram import F
from aiogram.types import Message as TgMessage
from maxapi.types import InputMedia

import config
from loader import tg_dp, tg_bot, max_bot

media_groups = {}

async def send_media_group(media_group_id: str):
    """
    Отправляет сгруппированные медиафайлы в MAX.
    """
    await asyncio.sleep(2)  # Ждем, пока соберутся все сообщения группы
    
    if media_group_id not in media_groups:
        return

    messages = media_groups.pop(media_group_id)
    messages.sort(key=lambda m: m.message_id)
    
    # Ищем текст (подпись) - берем первую непустую
    text = ""
    for m in messages:
        caption = m.caption or m.text
        if caption:
            text = caption
            break
            
    temp_files = []
    attachments = []
    
    try:
        for m in messages:
            if m.photo:
                photo = m.photo[-1]
                file_info = await tg_bot.get_file(photo.file_id)
                
                fd, temp_path = tempfile.mkstemp(suffix='.jpg')
                os.close(fd)
                temp_files.append(temp_path)
                
                await tg_bot.download_file(file_info.file_path, destination=temp_path)
                attachments.append(InputMedia(temp_path))
                
        if attachments:
            await max_bot.send_message(
                chat_id=config.MAX_CHANNEL_ID,
                text=text,
                attachments=attachments
            )
            logging.info(f"Forwarded media group {media_group_id} with {len(attachments)} items to MAX")
            
    except Exception as e:
        logging.error(f"Error forwarding media group {media_group_id}: {e}")
    finally:
        # Чистим временные файлы
        for path in temp_files:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logging.error(f"Error removing temp file {path}: {e}")


@tg_dp.channel_post(F.chat.id == config.TG_CHANNEL_ID)
async def on_channel_post(message: TgMessage):
    """
    Обрабатывает новые посты в Telegram канале и пересылает их в MAX.
    """
    logging.info(f"New post in Telegram channel {message.chat.id}: {message.message_id}")
    
    # Если это группа медиа
    if message.media_group_id:
        if message.media_group_id not in media_groups:
            media_groups[message.media_group_id] = []
            asyncio.create_task(send_media_group(message.media_group_id))
            
        media_groups[message.media_group_id].append(message)
        return

    # Обычная обработка одиночных сообщений
    text = message.text or message.caption or ""
    
    # Обработка фото
    if message.photo:
        # Берем фото самого лучшего качества
        photo = message.photo[-1]
        file_info = await tg_bot.get_file(photo.file_id)
        file_path = file_info.file_path
        
        # Скачиваем файл
        fd, temp_path = tempfile.mkstemp(suffix='.jpg')
        os.close(fd) 
        
        try:
            await tg_bot.download_file(file_path, destination=temp_path)
            
            # Отправляем в MAX
            media = InputMedia(temp_path)
            await max_bot.send_message(
                chat_id=config.MAX_CHANNEL_ID,
                text=text,
                attachments=[media]
            )
            logging.info("Forwarded photo to MAX")
            
        except Exception as e:
            logging.error(f"Error forwarding photo: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    # Обработка только текста
    elif text:
        try:
            await max_bot.send_message(
                chat_id=config.MAX_CHANNEL_ID,
                text=text
            )
            logging.info("Forwarded text to MAX")
        except Exception as e:
            logging.error(f"Error forwarding text: {e}")
