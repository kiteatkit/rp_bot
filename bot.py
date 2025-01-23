import telebot
from telebot import types

token = ''
bot = telebot.TeleBot(token)

# Список администраторов
admins = []  

# Словарь для хранения сообщений, ожидающих ответа
# Формат: {admin_id: {"user_id": user_id, "user_message": user_message}}
pending_replies = {}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    
    welcome_text = """
    Здравствуйте! 

Это бот для связи с администрацией.
    """
    bot.send_message(message.chat.id, welcome_text)
    
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    write_to_admin_button = types.KeyboardButton("Написать админу")
    keyboard.add(write_to_admin_button)
    
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "Написать админу")
def ask_for_message(message):
    msg = bot.send_message(message.chat.id, 'Введите свое сообщение или отправьте файл/картинку:')
    bot.register_next_step_handler(msg, forward_adm)

@bot.message_handler(content_types=["text", "photo", "document"])
def forward_adm(message):
    print('forward_adm')
    print(message.chat.id)
    
    if message.content_type == "text":
        for admin_id in admins:
            keyboard = types.InlineKeyboardMarkup()
            reply_button = types.InlineKeyboardButton(
                text="Ответить",
                callback_data=f"reply_{message.chat.id}"
            )
            keyboard.add(reply_button)
            
            bot.send_message(
                admin_id,
                f'Сообщение от пользователя {message.chat.id}:\n{message.text}',
                reply_markup=keyboard
            )
    
    elif message.content_type == "photo":
        for admin_id in admins:
            keyboard = types.InlineKeyboardMarkup()
            reply_button = types.InlineKeyboardButton(
                text="Ответить",
                callback_data=f"reply_{message.chat.id}"
            )
            keyboard.add(reply_button)
            
            caption = f'Фото от пользователя {message.chat.id}'
            if message.caption:  
                caption += f'\nОписание: {message.caption}'
            
            bot.send_photo(
                admin_id,
                message.photo[-1].file_id,  
                caption=caption,
                reply_markup=keyboard
            )

    elif message.content_type == "document":
        for admin_id in admins:
            keyboard = types.InlineKeyboardMarkup()
            reply_button = types.InlineKeyboardButton(
                text="Ответить",
                callback_data=f"reply_{message.chat.id}"
            )
            keyboard.add(reply_button)
            
            caption = f'Документ от пользователя {message.chat.id}'
            if message.caption: 
                caption += f'\nОписание: {message.caption}'
            
            bot.send_document(
                admin_id,
                message.document.file_id,
                caption=caption,
                reply_markup=keyboard
            )
    
    bot.send_message(message.chat.id, 'Ваше сообщение отправлено администраторам. Ожидайте ответа.')

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def handle_reply_button(call):
    admin_id = call.message.chat.id
    user_id = int(call.data.split("_")[1]) 
    
    pending_replies[admin_id] = user_id
    
    bot.send_message(admin_id, 'Введите ваш ответ:')
    bot.register_next_step_handler_by_chat_id(admin_id, send_reply_to_user)

def send_reply_to_user(message):

    admin_id = message.chat.id
    if admin_id in pending_replies:
        user_id = pending_replies[admin_id]
        bot.send_message(user_id, f'Ответ администратора:\n{message.text}')
        bot.send_message(admin_id, 'Ваш ответ отправлен пользователю.')
        
        
        del pending_replies[admin_id]
    else:
        bot.send_message(admin_id, 'Ошибка: не удалось найти пользователя для ответа.')

bot.infinity_polling()