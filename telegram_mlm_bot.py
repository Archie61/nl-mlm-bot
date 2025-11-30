# Telegram MLM-Bot для NL International (aiogram 3.x)
# Установить: pip install aiogram
# Использование: python telegram_mlm_bot_v3.py

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from datetime import datetime

# Конфигурация
API_TOKEN = '8523840701:AAE0sEIHd4wD5pOcR7v00KDl2eld6mhHtgA'  # Замените на ваш токен от BotFather
logging.basicConfig(level=logging.INFO)

# Инициализация бота
default_properties = DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
bot = Bot(token=API_TOKEN, default=default_properties)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния для сбора информации
class LeadStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_interest_level = State()
    waiting_for_email = State()

# База данных для хранения лидов (в реальном приложении использовать БД)
leads_database = []

# ============ ОСНОВНЫЕ КОМАНДЫ ============

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    """Приветственное сообщение"""
    welcome_text = """
👋 Добро пожаловать в MLM-Helper!

Я помогаю партнёрам NL International развивать их сетевой бизнес.

Выберите, что вас интересует:
"""
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="📋 Собрать контакт"), types.KeyboardButton(text="📚 О компании")],
        [types.KeyboardButton(text="💰 Структура дохода"), types.KeyboardButton(text="❓ FAQ")],
        [types.KeyboardButton(text="📊 Мои лиды"), types.KeyboardButton(text="⚙️ Помощь")]
    ], resize_keyboard=True)
    
    await message.answer(welcome_text, reply_markup=keyboard)

@dp.message(Command("help"))
async def send_help(message: types.Message):
    """Справка по командам"""
    help_text = """
📖 **Доступные команды:**

/start - Главное меню
/help - Эта справка
/about - Информация о NL International
/income - Структура доходов
/faq - Часто задаваемые вопросы
/stats - Статистика лидов

**Функции бота:**
✅ Сбор и квалификация потенциальных партнёров
✅ Хранение контактов
✅ Информация о продуктах
✅ Поддержка 24/7
"""
    await message.answer(help_text)

# ============ СБОР ЛИДОВ ============

@dp.message(F.text == "📋 Собрать контакт")
async def start_lead_collection(message: types.Message, state: FSMContext):
    """Начало процесса сбора контакта"""
    await message.answer("Спасибо за интерес! 😊\n\nДавайте соберём вашу информацию.\n\nКак вас зовут?", 
                       reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(LeadStates.waiting_for_name)

@dp.message(LeadStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Обработка имени"""
    await state.update_data(name=message.text, user_id=message.from_user.id, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    await message.answer("Спасибо! 👤\n\nТеперь укажите ваш номер телефона:")
    await state.set_state(LeadStates.waiting_for_phone)

@dp.message(LeadStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    """Обработка номера телефона"""
    await state.update_data(phone=message.text)
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="🔥 Высокий - готов начать сейчас")],
        [types.KeyboardButton(text="⭐ Средний - интересует информация")],
        [types.KeyboardButton(text="📌 Низкий - просто интересует")]
    ], resize_keyboard=True)
    
    await message.answer("Спасибо! 📞\n\nКаков ваш уровень интереса к бизнесу-возможности?", reply_markup=keyboard)
    await state.set_state(LeadStates.waiting_for_interest_level)

@dp.message(LeadStates.waiting_for_interest_level)
async def process_interest(message: types.Message, state: FSMContext):
    """Обработка уровня интереса"""
    data = await state.get_data()
    data['interest_level'] = message.text
    data['email'] = message.from_user.username or "N/A"
    
    # Сохраняем в базу
    leads_database.append(data)
    
    confirmation_text = f"""
✅ **Спасибо! Ваши данные сохранены:**

👤 Имя: {data['name']}
📞 Телефон: {data['phone']}
⭐ Интерес: {data['interest_level']}
⏰ Время: {data['timestamp']}

Что дальше?
"""
    
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="📚 Узнать о компании NL")],
        [types.KeyboardButton(text="💰 Структура доходов")],
        [types.KeyboardButton(text="🎯 Главное меню")]
    ], resize_keyboard=True)
    
    await message.answer(confirmation_text, reply_markup=keyboard)
    await state.clear()

# ============ ИНФОРМАЦИЯ О КОМПАНИИ ============

@dp.message(F.text.in_(["📚 О компании", "📚 Узнать о компании NL"]))
async def about_company(message: types.Message):
    """Информация о NL International"""
    about_text = """
🏢 **NL International**

**Кто мы:**
Международная компания с более чем 30-летним опытом в производстве высокачественной продукции для здоровья и красоты.

**Наши продукты:**
✅ Биологически активные добавки (БАД)
✅ Косметика и средства ухода
✅ Продукты питания
✅ Витамины и минералы

**Преимущества работы:**
💎 Высокий заработок (от 15% комиссии)
💎 Две линии доходов (продажи + структура)
💎 Бонусы и премии за достижения
💎 Возможность работы без вложений

**Как начать:**
1️⃣ Создать аккаунт
2️⃣ Купить товары для себя/вычета
3️⃣ Начать продавать и привлекать партнёров
4️⃣ Получать доход

Хотите узнать подробнее о доходах?
"""
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="💰 Структура доходов")],
        [types.KeyboardButton(text="🎯 Главное меню")]
    ], resize_keyboard=True)
    
    await message.answer(about_text, reply_markup=keyboard)

# ============ СТРУКТУРА ДОХОДОВ ============

@dp.message(F.text.in_(["💰 Структура дохода", "💰 Узнать о доходах"]))
async def income_structure(message: types.Message):
    """Информация о структуре доходов"""
    income_text = """
💰 **СТРУКТУРА ДОХОДОВ NL INTERNATIONAL**

**СТРОКА 1: ЛИЧНЫЕ ПРОДАЖИ**
📊 До 15% комиссии от всех ваших продаж
💡 Пример: вы продали на 10,000 руб → получите 1,500 руб

**СТРОКА 2: ДОХОД ОТ СТРУКТУРЫ**
📈 3-7% от продаж каждого привлечённого партнёра
📈 Доход растёт по мере расширения структуры

**ПРЕМИИ И БОНУСЫ:**
🏆 Еженедельные бонусы за объёмы
🏆 Ежемесячные премии лучшим партнёрам
🏆 Квартальные премии

**ПРИМЕР РАСЧЁТА:**
Вы привлекли 5 партнёров, каждый продаёт на 5,000 руб/месяц:
• Личные продажи: 5,000 × 15% = 750 руб
• От 5 партнёров: 25,000 × 5% = 1,250 руб
• **ИТОГО: 2,000 руб в месяц**

При расширении структуры до 50 человек доход может составить 50,000+ руб/месяц!

👉 Готовы начать?
"""
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="✅ Хочу начать")],
        [types.KeyboardButton(text="❓ Ещё вопросы")],
        [types.KeyboardButton(text="🎯 Главное меню")]
    ], resize_keyboard=True)
    
    await message.answer(income_text, reply_markup=keyboard)

# ============ FAQ ============

@dp.message(F.text.in_(["❓ FAQ", "❓ Ещё вопросы"]))
async def faq(message: types.Message):
    """Часто задаваемые вопросы"""
    faq_text = """
❓ **ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ**

**Q: Нужны ли мне деньги для старта?**
A: Нет, вы можете начать без вложений. Товары можно покупать постепенно.

**Q: Я не имею опыта в продажах, получится ли?**
A: Да! Мы обучим вас всему необходимому. Компания предоставляет материалы и поддержку.

**Q: Сколько времени нужно посвящать?**
A: Как вы сами решите. Можно работать 2-3 часа в день или полный рабочий день.

**Q: Когда я получу первый доход?**
A: При первой продаже. Обычно это происходит в первый же месяц.

**Q: Правда ли это МЛМ (сетевой маркетинг)?**
A: Да, это легальная форма бизнеса с реальными качественными продуктами.

**Q: Что если я не продам много?**
A: Даже небольшие продажи приносят доход. Главное - начать и быть последовательным.

**Q: Какой минимальный заказ?**
A: От 1,500 рублей на первый заказ.

Ещё есть вопросы? Свяжитесь с менеджером! 📞
"""
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="💬 Связаться с менеджером")],
        [types.KeyboardButton(text="🎯 Главное меню")]
    ], resize_keyboard=True)
    
    await message.answer(faq_text, reply_markup=keyboard)

# ============ СТАТИСТИКА ============

@dp.message(F.text.in_(["📊 Мои лиды", "📊 Статистика"]))
async def show_stats(message: types.Message):
    """Показать статистику собранных лидов"""
    user_leads = [lead for lead in leads_database if lead['user_id'] == message.from_user.id]
    
    stats_text = f"""
📊 **ВАША СТАТИСТИКА**

Всего собрано лидов: {len(user_leads)}

**По уровню интереса:**
"""
    
    if user_leads:
        high_interest = len([l for l in user_leads if "Высокий" in l.get('interest_level', '')])
        medium_interest = len([l for l in user_leads if "Средний" in l.get('interest_level', '')])
        low_interest = len([l for l in user_leads if "Низкий" in l.get('interest_level', '')])
        
        stats_text += f"""
🔥 Высокий интерес: {high_interest}
⭐ Средний интерес: {medium_interest}
📌 Низкий интерес: {low_interest}

**Последние лиды:**
"""
        for lead in user_leads[-5:]:
            stats_text += f"\n• {lead['name']} ({lead['timestamp']})"
    else:
        stats_text += "\nУ вас ещё нет собранных лидов. 📭\n\nСоберите первый контакт!"
    
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="📋 Собрать контакт")],
        [types.KeyboardButton(text="🎯 Главное меню")]
    ], resize_keyboard=True)
    
    await message.answer(stats_text, reply_markup=keyboard)

# ============ КОНТАКТЫ ============

@dp.message(F.text.in_(["💬 Связаться с менеджером", "⚙️ Помощь"]))
async def contact_manager(message: types.Message):
    """Контактная информация"""
    contact_text = """
📞 **СВЯЖИТЕСЬ С МЕНЕДЖЕРОМ**

**Телефон:** +7 (800) 555-35-35
**WhatsApp:** +7 (918) 555-35-35
**Email:** manager@nl-international.ru
**Telegram:** @nl_international_manager

🕐 Работаем с 9:00 до 21:00 (по МСК)
🗓️ 7 дней в неделю

Менеджер поможет вам:
✅ Ответит на все вопросы
✅ Расскажет о условиях
✅ Поможет с регистрацией
✅ Подберёт оптимальный пакет

Напишите менеджеру прямо сейчас! 💬
"""
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="🎯 Главное меню")]
    ], resize_keyboard=True)
    
    await message.answer(contact_text, reply_markup=keyboard)

# ============ ГЛАВНОЕ МЕНЮ ============

@dp.message(F.text == "🎯 Главное меню")
async def main_menu(message: types.Message):
    """Вернуться в главное меню"""
    await send_welcome(message)

# ============ ОСТАЛЬНОЕ ============

@dp.message(F.text == "✅ Хочу начать")
async def want_to_start(message: types.Message):
    """Пользователь хочет начать"""
    start_text = """
🎉 **ОТЛИЧНО! ДАВАЙТЕ НАЧНЁМ!**

Чтобы зарегистрироваться в системе:

1️⃣ Свяжитесь с менеджером по контактам ниже
2️⃣ Он создаст ваш личный кабинет
3️⃣ Выберите пакет на старт
4️⃣ Начните зарабатывать!

Нужна помощь менеджера? Нажмите кнопку ниже ⬇️
"""
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="💬 Связаться с менеджером")],
        [types.KeyboardButton(text="🎯 Главное меню")]
    ], resize_keyboard=True)
    
    await message.answer(start_text, reply_markup=keyboard)

@dp.message()
async def echo(message: types.Message):
    """Ответ на неизвестные сообщения"""
    echo_text = """
Я не совсем вас понял. 🤔

Выберите опцию из меню или напишите:
/help - для справки
/start - для главного меню
"""
    keyboard = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="📋 Собрать контакт"), types.KeyboardButton(text="📚 О компании")],
        [types.KeyboardButton(text="💰 Структура дохода"), types.KeyboardButton(text="❓ FAQ")],
        [types.KeyboardButton(text="🎯 Главное меню")]
    ], resize_keyboard=True)
    
    await message.answer(echo_text, reply_markup=keyboard)

# ============ ЗАПУСК БОТА ============

async def main():
    """Основная функция для запуска бота"""
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    print("✅ Бот успешно запущен!")
    asyncio.run(main())