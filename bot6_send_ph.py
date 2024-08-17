import requests
import xml.etree.ElementTree as ET
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from datetime import datetime, timedelta
import asyncio
import matplotlib.pyplot as plt
import os

API_TOKEN = '6851079900:AAEcLqzD-o5DLjH1uAgApTwwtn4a5w0AU0I'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# Путь к изображению
# PHOTO_PATH = '/home/alex/dragmet/1.png'

# Словарь для ассоциации кодов с названиями металлов
metal_codes = {
    "1": "Золото",
    "2": "Серебро",
    "3": "Платина",
    "4": "Палладий"
}

# Функция для получения курса металлов
def get_gold_rate(date_from, date_to):
    url = f"http://www.cbr.ru/scripts/xml_metall.asp?date_req1={date_from}&date_req2={date_to}"
    response = requests.get(url)
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        metal_rates = {}
        for record in root.findall('Record'):
            date = record.attrib['Date']
            code = record.attrib['Code']  # Извлекаем код металла
            metal_name = metal_codes.get(code, "Неизвестный металл")
            gold_rate = float(record.find('Buy').text.replace(",", "."))  # Преобразование курса в float
            
            if metal_name not in metal_rates:
                metal_rates[metal_name] = []
            metal_rates[metal_name].append((datetime.strptime(date, "%d.%m.%Y"), gold_rate))
        return metal_rates
    else:
        return None

# Функция для построения графиков и сохранения их локально
def plot_metal_rates(metal_rates):
    images = []
    for metal, data in metal_rates.items():
        dates, rates = zip(*data)
        plt.figure(figsize=(10, 6))
        plt.plot(dates, rates, marker='o', markersize=5, linewidth=1, label=metal)  # Изменена точка и линия
        plt.title(f'Курс {metal} за выбранный период')
        plt.xlabel('Дата')
        plt.ylabel('Курс (руб./грамм)')
        plt.grid(True)
        plt.legend()
        
        image_path = f'{metal}.png'
        plt.savefig(image_path)
        images.append(image_path)
        plt.close()
    return images

# Обработчик команды /start для показа меню
@router.message(Command("start"))
async def send_menu(message: types.Message):
    # Создаем кнопки для меню
    button1 = KeyboardButton(text="За последний месяц")
    button2 = KeyboardButton(text="За последние 3 месяца")
    button3 = KeyboardButton(text="За последние полгода")
    button4 = KeyboardButton(text="За последний год")
    button5 = KeyboardButton(text="За последние 3 года")  # Новая кнопка
    
    # Создаем меню с кнопками
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [button1, button2],
            [button3, button4],
            [button5]  # Добавляем новую кнопку
        ],
        resize_keyboard=True
    )
    
    await message.answer("Выберите действие:", reply_markup=markup)

@router.message(lambda message: message.text in ["За последний месяц", "За последние 3 месяца", "За последние полгода", "За последний год", "За последние 3 года"])
async def handle_period_selection(message: types.Message):
    today = datetime.today()
    
    if message.text == "За последний месяц":
        date_from = (today - timedelta(days=30)).strftime("%d/%m/%Y")
    elif message.text == "За последние 3 месяца":
        date_from = (today - timedelta(days=90)).strftime("%d/%m/%Y")
    elif message.text == "За последние полгода":
        date_from = (today - timedelta(days=180)).strftime("%d/%m/%Y")
    elif message.text == "За последний год":
        date_from = (today - timedelta(days=365)).strftime("%d/%m/%Y")
    elif message.text == "За последние 3 года":
        date_from = (today - timedelta(days=365*3)).strftime("%d/%m/%Y")
    
    date_to = today.strftime("%d/%m/%Y")
    metal_rates = get_gold_rate(date_from, date_to)
    
    if metal_rates:
        images = plot_metal_rates(metal_rates)
        for image in images:
            # Используем путь к файлу для создания InputFile
            await message.reply_photo(photo=types.FSInputFile(path=image))
            os.remove(image)  # Удаляем файл после отправки
    else:
        await message.reply("Не удалось получить данные о курсах металлов.")

async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
