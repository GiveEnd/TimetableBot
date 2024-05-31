from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
from create_bot import dp, bot
from data_base import sqlite_db
from keyboards import admin_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ID = None

class FSMAdmin(StatesGroup):
    date = State()
    time = State()
    name = State()

#Получаем ID текущего модератора
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id,'Что надо хозяин?', reply_markup = admin_kb.button_case_admin)
    await message.delete()
    
    read = await sqlite_db.sql_read2()
    print("Other",read)

#Начало диалога загрузки нового пункта меню
async def cm_start(message : types.Message):    
    if message.from_user.id == ID:  
       await FSMAdmin.next()
       await message.reply('Напишите дату в формате: yyyy-mm-dd')

 #Выход из состояний    
async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
       current_state = await state.get_state()
       if current_state is None:
          return
       await state.finish()
       await message.reply('OK')       

#Первый ответ и пишем в словарь
async def load_date(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
       async with state.proxy() as data:
                  data['date'] = message.text
                  await FSMAdmin.next()
                  await message.reply('Введите время')   

 #Второй ответ
async def load_time(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
       async with state.proxy() as data:
                  data['time'] = message.text
                  await FSMAdmin.next()
                  await message.reply('Введите название')

#Третий ответ
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
       async with state.proxy() as data:
                  data['name'] = message.text         

    await sqlite_db.sql_add_command(state)
    await state.finish() 
    await message.reply('Занятие добавлено')   

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(callback_query: types.CallbackQuery):
     await sqlite_db.sql_delete_command(callback_query.data.replace('del ', ''))
     await callback_query.answer(text = f'{callback_query.data.replace("del ", "")} Удалено.', show_alert = True)

async def delete_item(message: types.Message):
     if message.from_user.id == ID:
          read = await sqlite_db.sql_read2()
          for ret in read:
               await bot.send_message(message.from_user.id, text = ret, reply_markup = InlineKeyboardMarkup().add(InlineKeyboardButton(f'Удалить', callback_data = f'del {ret[0]}')))     

#Регистрация хэндлеров
def register_handlers_admin(dp : Dispatcher):
    dp.register_message_handler(cm_start, commands = ['Загрузить'], state = None)
    dp.register_message_handler(cancel_handler, state = '*', commands = 'отмена')
    dp.register_message_handler(cancel_handler, Text(equals = 'отмена', ignore_case = True), state = '*')
    dp.register_message_handler(load_date, state = FSMAdmin.date)
    dp.register_message_handler(load_time, state = FSMAdmin.time)
    dp.register_message_handler(load_name, state = FSMAdmin.name)
    dp.register_message_handler(make_changes_command, commands = ['moderator'], is_chat_admin = True)
    dp.register_message_handler(delete_item, commands = 'Удалить')