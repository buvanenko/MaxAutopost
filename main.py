import asyncio
import logging

from loader import max_dp, max_bot, tg_dp, tg_bot
import handlers.max_handlers
import handlers.tg_handlers

logging.basicConfig(level=logging.INFO)

async def main():
    logging.info("Starting bots...")
    # Запускаем обоих ботов параллельно
    await asyncio.gather(
        max_dp.start_polling(max_bot),
        tg_dp.start_polling(tg_bot)
    )

if __name__ == '__main__':
    asyncio.run(main())