from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_calories = KeyboardButton('Рассчитать норму калорий')
button_info = KeyboardButton(text='Информация')
button_formula = KeyboardButton('Формулы расчёта')
button_buy = KeyboardButton('Купить')
kb.add(button_calories, button_info)
kb.add(button_buy, button_formula)

kb_buy = InlineKeyboardMarkup(resize_keyboard=True)
button_buy1 = InlineKeyboardButton('Продукт 1', callback_data='product_buying')
button_buy2 = InlineKeyboardButton('Продукт 2', callback_data='product_buying')
button_buy3 = InlineKeyboardButton('Продукт 3', callback_data='product_buying')
button_buy4 = InlineKeyboardButton('Продукт 4', callback_data='product_buying')
kb_buy.row(button_buy1, button_buy2, button_buy3, button_buy4)


@dp.message_handler(commands='start')
async def start(message):
    await message.answer(text='Вас приветствует калькулятор калорий', reply_markup=kb)


@dp.message_handler(text='Информация')
async def info(message):
    await message.answer(text='Вас приветствует калькулятор калорий '
                              'в котором вы можете рассчитать и понять сколько нужно калорий '
                              'в день именно Вам')


@dp.message_handler(text='Формулы расчёта')
async def get_formulas(call):
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5 '
                              'для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for i in range(1, 5):
        with open('img.jpg', 'rb') as img:
            await message.answer_photo(img, f'Название: Product{i} | Описание: описание {i} | Цена: {i * 100}')
    await message.answer('Выберите продукт для покупки:', reply_markup=kb_buy)


@dp.callback_query_handler(text=['product_buying'])
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text=['calories'])
async def set_age(call):
    await call.message.answer('Введите свой возраст')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    calories = int(data['weight']) * 10 + int(data['growth']) * 6.25 - int(data['age']) * 5
    await message.answer(f'Ваша норма калорий: {calories}')

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
