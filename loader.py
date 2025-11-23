from maxapi import Bot as MaxBot, Dispatcher as MaxDispatcher
from aiogram import Bot as TgBot, Dispatcher as TgDispatcher
import config

# Initialize Bots
max_bot = MaxBot(token=config.MAX_BOT_TOKEN)
max_dp = MaxDispatcher()

tg_bot = TgBot(token=config.TELEGRAM_BOT_TOKEN)
tg_dp = TgDispatcher()
