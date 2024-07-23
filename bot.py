from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, BotCommand, KeyboardButton, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, JobQueue, CallbackContext, ConversationHandler
from datetime import datetime, timedelta
import logging
from lorabot.lorabot import LoraBot
import re

lora_bot = LoraBot("AnalyticBot")


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)




TOKEN = '7478620467:AAGy8feFTv0JCECsYGpPuhDsk_T-K3O_ZfE'

ASK_PASSWORD, ASK_DATE, ANALYTIC_MODE, ASK_DATE_START, ASK_DATE_END, ANALYTICS_DATA = range(6)

notifications_sent = {}
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    return ConversationHandler.END

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на инлайн-кнопки"""

    query = update.callback_query
    await query.answer()

    # обрабатывать нажатия на кнопки
    choice = query.data
    if choice == 'https://rabota.ykt.ru':
        lora_bot.event('Нажато "Сайт" в уведомлении:', 'Уведомления', update.effective_chat.id)
        

    await query.edit_message_text(text=f"{choice}")

async def send_notification(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id
    await context.bot.send_photo(chat_id, photo=open('lorabot\screens\img_not_1.png', 'rb'),caption=f"По вашему запросу появились 4 новые вакансии 💼")
    keyboard = [[InlineKeyboardButton("Сайт", callback_data='https://rabota.ykt.ru')]] 
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id,"Для просмотра нажмите кнопку сайт.",reply_markup=reply_markup)

async def send_notification_2(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id
    await context.bot.send_photo(chat_id, photo=open('lorabot\screens\img_not_1.png', 'rb'),caption=f"По вашему запросу появились 2 новые вакансии 💼")
    keyboard = [[InlineKeyboardButton("Сайт", callback_data='https://rabota.ykt.ru')]] 
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id,"Для просмотра нажмите кнопку сайт.",reply_markup=reply_markup)

async def send_notification_3(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id
    text= 'Благодарим за Ваше содействие  в тестировании Telegram-бота от Ykt.ru. Ваша поддержка очень важна для нас.'
    text2= 'Пока мы работаем над новыми функциями.Вы можете оставить свои пожелания в этой форме'
    await context.bot.send_photo(chat_id, photo=open('lorabot\screens\img_not_2.png', 'rb'),caption=text)
    keyboard = [[InlineKeyboardButton("Ссылка", callback_data='https://forms.yandex.ru/u/668f517273cee7bd009f76b6/')]] 
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id,text2,reply_markup=reply_markup)

async def analytics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['Events'] = False 
    context.user_data['Users'] = False
    context.user_data['start_period'] = None 
    context.user_data['end_period'] = None
    if 'analytic_mode' in context.user_data and context.user_data['analytic_mode']:
        if update.message.text == 'Events':
            context.user_data['Events'] = True
            keyboard = [[KeyboardButton("Да"), KeyboardButton("Нет") ],]
            reply_markup_keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text('Вы выбрали анализ событий. Хотите ли ввести период анализа?', reply_markup=reply_markup_keyboard)
            return ASK_DATE
        elif update.message.text == 'Users':
            context.user_data['Users'] = True 
            keyboard = [[KeyboardButton("Да"), KeyboardButton("Нет") ],]
            reply_markup_keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text('Вы выбрали анализ пользователей. Хотите ли ввести период анализа?', reply_markup=reply_markup_keyboard)
            return ASK_DATE
        else:
            await context.bot.send_message(update.effective_chat.id,'Введите /start и попробуйте снова')
            return ConversationHandler.END
    else:
        await context.bot.send_message(update.effective_chat.id, 'Введите пароль')
        return ASK_PASSWORD

async def analytics_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    date_start = context.user_data['start_period']
    date_end = context.user_data['end_period']
    user_id = update.effective_chat.id
    text = update.message.text
    if context.user_data['Users']:
        if text == "Ежедневные уникальные пользователи":
            photo_new_users, info_new_users = lora_bot.analyze_new_user(period_start=date_start, period_end=date_end)
            await context.bot.send_message(update.effective_chat.id, info_new_users)
            await context.bot.send_photo(user_id, photo=photo_new_users,caption=f"Количество уникальных пользователей")
            photo_accum, info_new_users_accum = lora_bot.analyze_user_number_accumulation(period_start=date_start, period_end=date_end)
            await context.bot.send_message(update.effective_chat.id, info_new_users_accum)
            await context.bot.send_photo(user_id, photo=photo_accum,caption=f"Количество уникальных пользователей с накоплением")
            return ANALYTICS_DATA
            
        if text == "Количество активных пользователей в день":
            photo_users_dau, info_users_dau = lora_bot.analyze_dau(period_start=date_start, period_end=date_end)
            await context.bot.send_message(update.effective_chat.id, info_users_dau)
            await context.bot.send_photo(user_id, photo=photo_users_dau,caption=f"Количество активных пользователей по дням")
            return ANALYTICS_DATA
        if text == "Total":
            info_total = lora_bot.analyze_total(period_start=date_start, period_end=date_end)
            await context.bot.send_message(update.effective_chat.id, info_total)
            return ANALYTICS_DATA
        if text == "Число сообщений от пользователей в день":
            photo_messages_number, info_messages_number = lora_bot.analyze_messages_number(period_start=date_start, period_end=date_end)
            await context.bot.send_message(update.effective_chat.id, info_messages_number)
            await context.bot.send_photo(user_id, photo=photo_messages_number,caption=f"Количество сообщений пользователей по дням")
            return ANALYTICS_DATA
        if text == "Анализ всех сообщений":
            info_messages = lora_bot.analyze_messages(period_start=date_start, period_end=date_end, volume=100)
            await context.bot.send_message(update.effective_chat.id, info_messages)
            return ANALYTICS_DATA
        if text == "Анализ типа сообщений":
            photo_messages_type, info_messages_type = lora_bot.analyze_messages_type(period_start=date_start, period_end=date_end)
            await context.bot.send_message(update.effective_chat.id, info_messages_type)
            await context.bot.send_photo(user_id, photo=photo_messages_type,caption=f"Тип сообщений пользователей")
            return ANALYTICS_DATA
        keyboard = [
        [KeyboardButton("Ежедневные уникальные пользователи")],
        [KeyboardButton("Количество активных пользователей в день")],
        [KeyboardButton("Total")],
        [KeyboardButton("Число сообщений от пользователей в день")],
        [KeyboardButton("Анализ всех сообщений")],
        [KeyboardButton("Анализ типа сообщений")]
        ]
        reply_markup_keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text('Выберите анализ', reply_markup=reply_markup_keyboard)

        return ANALYTICS_DATA
    elif context.user_data['Events']:
        if text == "Список основных событий и их количество":
            info_events = lora_bot.analyze_events(period_start=date_start,period_end=date_end,volume=100)
            await context.bot.send_message(update.effective_chat.id, info_events)
            return ANALYTICS_DATA
        if text == "Количество событий по дням":
            photo_events_number, info_events_number= lora_bot.analyze_events_number(period_start=date_start, period_end=date_end)
            await context.bot.send_message(update.effective_chat.id, info_events_number)
            await context.bot.send_photo(user_id, photo=photo_events_number,caption=f"Количество событий по дням")
            return ANALYTICS_DATA
        if text == "Анализ типа событий":
            photo_messages_type, info_messages_type = lora_bot.analyze_events_type(period_start=date_start, period_end=date_end)
            await context.bot.send_message(update.effective_chat.id, info_messages_type)
            await context.bot.send_photo(user_id, photo=photo_messages_type,caption=f"Анализ типа событий")
            return ANALYTICS_DATA    
        keyboard = [
        [KeyboardButton("Список основных событий и их количество")],
        [KeyboardButton("Анализ типа событий")],
        [KeyboardButton("Количество событий по дням")]
        
        ]
        reply_markup_keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text('Выберите анализ', reply_markup=reply_markup_keyboard)
        return ANALYTICS_DATA

async def ask_date_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    date = update.message.text

    if bool(re.match(r'^\d{4}-\d{2}-\d{2}$',date)):
        context.user_data['end_period'] = date
        await context.bot.send_message(update.effective_chat.id, 'Вы ввели конец даты')
        return ANALYTICS_DATA
    else:
        await context.bot.send_message(update.effective_chat.id, 'Неверный формат. Введите заново(отмена /cancel)')
        return ASK_DATE_END
async def ask_date_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    date = update.message.text
    if bool(re.match(r'^\d{4}-\d{2}-\d{2}$',date)):
        context.user_data['start_period'] = date
        await context.bot.send_message(update.effective_chat.id, 'Введите конец в формате YYYY-MM-DD')
        return ASK_DATE_END
    else:
        await context.bot.send_message(update.effective_chat.id, 'Неверный формат. Введите заново(отмена /cancel)')
        return ASK_DATE_START        

async def ask_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text
    if answer == 'Да':
        await context.bot.send_message(update.effective_chat.id, 'Введите начало в формате YYYY-MM-DD')
        return ASK_DATE_START
    elif answer == 'Нет':
        await context.bot.send_message(update.effective_chat.id, 'Вы выбрали режим без даты. Введите что угодно для открытия меню')
        return ANALYTICS_DATA
    else:
        return ConversationHandler.END
async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_password = update.message.text
    if query_password =='lorabot':
        context.user_data['analytic_mode'] = True
        await context.bot.send_message(update.effective_chat.id,'Вы активировали режим анатилики.')
        keyboard = [
        [KeyboardButton("Events"), KeyboardButton("Users") ],     
        ]
        reply_markup_keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text('Выбери то, что хочешь проанализировать', reply_markup=reply_markup_keyboard)
        return ANALYTIC_MODE
    else:
        await context.bot.send_message(update.effective_chat.id,'Неверный пароль')
        return ConversationHandler.END

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:  
    user_id = update.effective_chat.id
    context.user_data['analytic_mode'] = False
    #для отслеживания новых пользователей
    lora_bot.user(user_id, update.message.from_user.language_code)

    #для отслеживания команд, сообщений из меню и обычных сообщений

    # lora_bot.message(TEXT, TEXT_TYPE, user_id)

    #для отслеживания событий
    lora_bot.event('Команда старт', 'command', update.effective_chat.id)



    text_start = "Я чат бот сервиса RabotaYkt.ru🌱. \nЧем могу помочь? \nЯ могу приступить к поиску вакансий или управлять вашими подписками."
    # context.user_data['p_start'] = '2024-07-16' 
    # context.user_data['p_end']= '2024-07-16' 

    
    # info_total = lora_bot.analyze_total()
    # await context.bot.send_message(update.effective_chat.id, info_total) 

    # photo_events_number, info_events_number = lora_bot.analyze_events_number()
    # await context.bot.send_message(update.effective_chat.id, info_events_number)
    # await context.bot.send_photo(user_id, photo=photo_events_number,caption=f"Количество событий по дням")

    # photo_new_users, info_new_users = lora_bot.analyze_new_user()
    # await context.bot.send_message(update.effective_chat.id, info_new_users)
    # await context.bot.send_photo(user_id, photo=photo_new_users,caption=f"Количество оригинальных пользователей")

    # photo_accum, info_new_users_accum = lora_bot.analyze_user_number_accumulation()
    # await context.bot.send_message(update.effective_chat.id, info_new_users_accum)
    # await context.bot.send_photo(user_id, photo=photo_accum,caption=f"Количество оригинальных пользователей с накоплением")

    # photo_users_dau, info_users_dau = lora_bot.analyze_dau()
    # await context.bot.send_message(update.effective_chat.id, info_users_dau)
    # await context.bot.send_photo(user_id, photo=photo_users_dau,caption=f"Количество активных пользователей по дням")

    # photo_users_activity, info_users_activity = lora_bot.analyze_hour_activity()
    # await context.bot.send_message(update.effective_chat.id, info_users_activity)
    # await context.bot.send_photo(user_id, photo=photo_users_activity,caption=f"Активность пользователей в течении дня")

    user_id = update.effective_chat.id
  

    for key in context.user_data: # Сброс всех ключей
        if key == 'count_yes' or key == 'user_id':
            continue 
        context.user_data[key] = False

    if 'count_yes' not in context.user_data:
        context.user_data['count_yes'] = 0

    keyboard = [
        [KeyboardButton("Поиск вакансий🔍")],
        [KeyboardButton("Мои подписки📑")],
        [KeyboardButton("Сайт🔗")],
        [KeyboardButton("Помощь🙏🏻")]
        
    ]
    reply_markup_keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(text_start, reply_markup=reply_markup_keyboard)



async def message_find_vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text_find_vac = 'Какую вакансию вы ищете?\nВыберите или введите категорию'
    lora_bot.event('Поиск вакансий', 'command', update.effective_chat.id)
    keyboard = [
        [KeyboardButton("Подработка💸"), KeyboardButton("Продавец🛒") ],
        [KeyboardButton("Инженер🧑🏻‍🔧"), KeyboardButton("Разработчик👨🏻‍💻")],
        [KeyboardButton("в начало")]        
    ]
    context.user_data['find_vac_x'] = True
    reply_markup_keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(text_find_vac, reply_markup=reply_markup_keyboard)

async def message_my_subs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lora_bot.event('Мои подписки', 'menu', update.effective_chat.id)

    text_my_subs = f'У вас сейчас {context.user_data["count_yes"]} подписок на вакансии. Мы пришлем вам уведомление, как только появится новая вакансия'
    await update.message.reply_text(text_my_subs)

async def message_site(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lora_bot.event('Запрос сайта', 'menu', update.effective_chat.id)
    text_site = 'Вот ссылка на наш сервис: https://rabota.ykt.ru'
    await update.message.reply_text(text_site)

async def message_help_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lora_bot.event('Помощь', 'menu', update.effective_chat.id)
    text_help_me = 'Напишите ваше обращение для помощи на эту гугл-форму обратной связи🔗: https://forms.yandex.ru/u/668f517273cee7bd009f76b6/'
    await update.message.reply_text(text_help_me)

async def message_salary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text_salary = 'Выберите нужную вам зарплату или введите свое значение💸'
    keyboard = [
        [KeyboardButton("от 30 000"), KeyboardButton("от 50 000") ],
        [KeyboardButton("от 80 000"), KeyboardButton("от 100 000")],
        [KeyboardButton("пропустить"), KeyboardButton("в начало")]        
    ]
    context.user_data['salary_vac_x'] = True
    reply_markup_keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(text_salary, reply_markup=reply_markup_keyboard)

async def message_oops(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text_oops1 = 'Упс, произошла ошибка с сервером... Мы уже работаем над устранением данной ошибки.'
    text_oops2 = '❓Хотите сохранить поиск и подписаться на вакансию?'

    keyboard = [
        [KeyboardButton("да🙋🏻‍♂️"), KeyboardButton("нет🙅🏻‍♂️") ],
        [ KeyboardButton("в начало")]        
    ]
    context.user_data['oops_x'] = True
    reply_markup_keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(text_oops1)
    await update.message.reply_text(text_oops2, reply_markup=reply_markup_keyboard)







async def handle_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    lora_bot.message(text, 'Сообщение пользователя', update.effective_chat.id)
    lora_bot.event('Сообщение пользователя', 'text', update.effective_chat.id)
    if text.lower() == "в начало" :
        await start(update,context)
        return
    
    if 'find_vac_x' in context.user_data and context.user_data['find_vac_x']:
        await message_salary(update,context)
        context.user_data['find_vac_x'] = False
        return
    
    if 'salary_vac_x' in context.user_data and context.user_data['salary_vac_x']:
        await message_oops(update,context)
        context.user_data['salary_vac_x'] = False
        return
    if 'oops_x' in context.user_data and context.user_data['oops_x']:
        
        if text == 'да🙋🏻‍♂️' or 'да':
            text_oops = ' Ваш запрос сохранен. Мы отправим вам уведомление, как только появятся новые вакансии по вашему запросу😉.\nВы будете одним из первых, кто увидит эту вакансию.'
            context.user_data['count_yes'] = context.user_data['count_yes'] + 1
            user_id = update.effective_chat.id
            lora_bot.event('Количество нажатий на кнопку "Да" в подписке на обновления', 'menu', update.effective_chat.id)
            if not notifications_sent.get(user_id, False):
                target_hours_1 = timedelta(hours=24)
                target_hours_2 = timedelta(hours=72)
                target_hours_3 = timedelta(hours=78)
                context.job_queue.run_once(send_notification, target_hours_1, chat_id=user_id, name=str(user_id), data=target_hours_1)
                context.job_queue.run_once(send_notification_2, target_hours_2, chat_id=user_id, name=str(user_id), data=target_hours_2)
                context.job_queue.run_once(send_notification_3, target_hours_3, chat_id=user_id, name=str(user_id), data=target_hours_3)
                notifications_sent[user_id] = True
                    

        if text == 'нет🙅🏻‍♂️' or 'нет':
            text_oops = 'Можете начать новый поиск🔍 или перейти на наш официальный сайт🔗'
        await update.message.reply_text(text_oops)
        context.user_data['oops_x'] = False   
        return

    if  text == "Поиск вакансий🔍":
        await message_find_vacancies(update,context)
    elif text == "Мои подписки📑":
        await message_my_subs(update,context)
        
    elif text == "Сайт🔗":
        await message_site(update,context)
    elif text == "Помощь🙏🏻":
        await message_help_me(update,context)
    else:
        await update.message.reply_text("Я вас не понимаю. Вы можете вернуться в стартовое меню командой /start.")


def main():
    # Создаем Application и передаем ему токен бота.
    application = Application.builder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('analytics', analytics)],
        states={
            ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_password)],
            ASK_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date)],
            ANALYTIC_MODE:[MessageHandler(filters.TEXT & ~filters.COMMAND, analytics)],
            ASK_DATE_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date_start)],
            ASK_DATE_END: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_date_end)],
            ANALYTICS_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, analytics_data)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    # Обработчик всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_keyboard))

    application.add_handler(CallbackQueryHandler(button))

    # Запускаем бота
    application.run_polling()
    
    

if __name__ == '__main__':
    main()
