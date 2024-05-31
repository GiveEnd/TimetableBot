from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from create_bot import bot
from data_base import sqlite_db

async def command_start(message : types.Message):
    try:
        # Создаем inline кнопки
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('Расписание событий', callback_data='menu'))
        kb.add(InlineKeyboardButton('Расположение', callback_data='place'))

        # Отправляем приветственное сообщение с inline кнопками и сохраняем его message_id
        welcome_message = await bot.send_message(message.from_user.id, 'Здравствуйте!', reply_markup=kb)
        await message.delete()

        # Сохраняем message_id приветственного сообщения в пользовательских данных
        await bot.send_chat_action(message.chat.id, 'typing')
        await bot.send_message(message.from_user.id, 'Привет! Я бот с расписанием!', reply_markup=kb)
        await bot.delete_message(chat_id=welcome_message.chat.id, message_id=welcome_message.message_id)
    except:
        await message.reply('Общение с ботом через ЛС, напишите ему:\nhttps://t.me/TestPizzzzzzaBot')

async def on_callback_query(callback_query: types.CallbackQuery):
    List_data = await sqlite_db.sql_date_out()

    if callback_query.data == 'place':
        await bot.edit_message_text('Расположение: бул. Гагарина, 20', chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('Главное меню', callback_data='back'))  # Добавляем кнопку "Главное меню"
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=kb)

    elif callback_query.data == 'menu':
        kb = InlineKeyboardMarkup()

        for item in List_data:
            kb.add(InlineKeyboardButton(text=item, callback_data=f'menu_{item}'))
  
        kb.add(InlineKeyboardButton('Главное меню', callback_data='back'))  # Добавляем кнопку "Главное меню"
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=kb)
        
    elif callback_query.data.startswith('menu_'):
         for data in List_data:
             if callback_query.data == 'menu_' + data:
                List_name = await sqlite_db.sql_list_name(data)
                kb = InlineKeyboardMarkup()
                for item in List_name:
                    kb.add(InlineKeyboardButton(text=item.split("|")[2], callback_data=f'list_{item}'))
                kb.add(InlineKeyboardButton('Главное меню', callback_data='back'))  # Добавляем кнопку "Главное меню"
                await bot.edit_message_text("Расписание на " + data + ".\n\nВыбери событие, о котором ты хочешь получить напоминание, и нажми на его название:", chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=kb)                 

    elif callback_query.data.startswith('list_'):
        button_text = callback_query.inline_message_id  # Используем идентификатор инлайн сообщения в качестве button_text
        callback_data = callback_query.data
        print(callback_query.data.split("|")[1]) 
     # Получаем текст и данные обратного вызова (callback_data) из всех кнопок
    elif callback_query.data == 'back':
        # Добавляем кнопку "Главное меню" и возвращаемся в главное меню
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('Расписание событий', callback_data='menu'))
        kb.add(InlineKeyboardButton('Расположение', callback_data='place'))
        await bot.edit_message_text('Привет! Я бот с расписанием!', chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=kb)


def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_callback_query_handler(on_callback_query)
