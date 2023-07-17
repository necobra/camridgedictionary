import random

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram import Bot, Dispatcher, executor, types
from random import randint
from aiogram.dispatcher.filters import Text

bot = Bot(token='6359914217:AAF-dXglsAl5swZnrFtFOe4qSp7dnIZWcsg', parse_mode='html')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler()
async def process_words(message: types.Message):
    words_list = message.text.split('\n')
    # print(words_list)
    if words_list[-1] == '1':
        msg = await translate(words_list)
    else:
        msg = ""
        for word in words_list:
            msg += 'https://dictionary.cambridge.org/dictionary/english/'+word+'\n'+'\n'

    await bot.send_message(message.chat.id, msg, disable_web_page_preview=True)


async def translate(words_list):
    from googletrans import Translator
    msg = ""
    translator = Translator()
    for word in words_list[:-1]:
        translated_text = translator.translate(word, dest='uk')
        print(translated_text.text)
        msg += translated_text.text + '\n'
    return msg

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
