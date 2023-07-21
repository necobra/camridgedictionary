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


class Form(StatesGroup):
    spelling_guess = State()


async def shuffle_lists(array1, array2):
    # Визначаємо порядок перемішування для одного з масивів
    random_order = random.sample(range(len(array1)), len(array1))

    # Застосовуємо отриманий порядок перемішування до обох масивів
    shuffled_array1 = [array1[i] for i in random_order]
    shuffled_array2 = [array2[i] for i in random_order]

    print("Shuffled Array 1:", shuffled_array1)
    print("Shuffled Array 2:", shuffled_array2)

    return shuffled_array1, shuffled_array2


@dp.message_handler()
async def process_words(message: types.Message, state: FSMContext):
    words_list = message.text.split('\n')
    # print(words_list)

    # remove first number
    if words_list[0].isdigit():
        words_list = words_list[1:]

    # select type of action
    if words_list[-1] == '1':
        # 1 - translate
        msg = "\n".join((await translate(words_list))[:-1])
    elif words_list[-1] == '2':
        # 2 - mini-game: guess english spelling from ukrainian tranlation
        translated_words_list = await translate(words_list)
        translated_words_list, words_list = await shuffle_lists(translated_words_list[:-1], words_list[:-1])
        msg = 'Переклад: ' + translated_words_list[0] + '\nНапишіть правильне написання слова англійською:\n' \
                                                        'Якщо хочете закінчити напишіть /end'
        await Form.spelling_guess.set()
        async with state.proxy() as qdata:
            qdata['translated_words_list'] = translated_words_list
            qdata['words_list'] = words_list
            qdata['i'] = 0

    else:
        # default - urls to words
        msg = ""
        for word in words_list:
            msg += 'https://dictionary.cambridge.org/dictionary/english/'+word+'\n'+'\n'

    await bot.send_message(message.chat.id, msg, disable_web_page_preview=True)


@dp.message_handler(state=Form.spelling_guess)
async def spelling_guess(message: types.Message, state: FSMContext):
    async with state.proxy() as qdata:
        i = qdata['i']
        qdata['i'] += 1
        translated_words_list = qdata['translated_words_list']
        words_list = qdata['words_list']

    if message.text == '/end':
        msg = 'the end'
        await bot.send_message(message.chat.id, msg)
        await state.finish()
        return

    ans = words_list[i]
    if message.text == ans:
        msg = "answer is correct🎉"
    else:
        msg = 'correct answer is ' + ans
    await bot.send_message(message.chat.id, msg)

    if i == len(translated_words_list) - 1:
        msg = 'the end'
        await bot.send_message(message.chat.id, msg)
        await state.finish()
        return

    msg = 'Переклад: ' + translated_words_list[i+1] + '\nНапишіть правильне написання слова англійською:\n'
    await bot.send_message(message.chat.id, msg)


async def translate(words_list):
    from googletrans import Translator
    translated_words_list = []
    translator = Translator()
    for word in words_list:
        translated_text = translator.translate(word, dest='uk')
        # print(translated_text.text)
        translated_words_list.append(translated_text.text)
    return translated_words_list


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
