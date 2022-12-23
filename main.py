import os
import time

from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram import Bot, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import config
from aiogram.types import InputFile, CallbackQuery
from bs4 import BeautifulSoup
import wget, lxml
import gspread

worksheet = gspread.service_account(filename='level-slate-280111-4930953f5702.json').open_by_url('https://docs.google.com/spreadsheets/d/1m2O23ai-s83iNdPOOn4cLtHwc5Ciw82-RJvwW2gIvrk/edit#gid=0').get_worksheet(0)
bot = Bot(token=config.TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)

inline = InlineKeyboardMarkup().add(InlineKeyboardButton(' ✅', callback_data='post'))
def postPhoto(title):
    if "STABLE" in title:
        photo = InputFile('files/stable_build.jpg')
    else:
        photo = InputFile('files/weekly_build.jpg')
    return photo
def postText(title):
    if "STABLE" in title:
        type = "STABLE"
        posttext = '<a href="https://t.me/xiaomieu_channel">channel</a> | <a href="https://t.me/xiaomieu_chat">chat</a> | #stable'
    else:
        type = "WEEKLY"
        posttext = '<a href="https://t.me/xiaomieu_channel">channel</a> | <a href="https://t.me/xiaomieu_chat">chat</a> | #weekly'

    y = title.find('V')
    if "fastboot" in title:
        version = title[y:-29]
    else:
        version = title[y:-20]
    x = 2
    while (True):
        if x % 10 == 0:
            time.sleep(4)
        if str(worksheet.acell(f'A{x}').value).upper() in title.upper():
            name = worksheet.acell(f'B{x}').value
            break
        x = x + 1
        print(x)

    link = title

    text = f"Обновление {type} | {version} доступно для {name}\n\n{link}\n\n{posttext}"
    return text
async def post():
    with open("sorce.html", "r") as f:
        index = f.read()
    soup = BeautifulSoup(index, "lxml")
    title = soup.find("item").find("title").text
    text = postText(soup.find("item").find("link").text)
    photo = postPhoto(soup.find("item").find("link").text)
    f.close()
    os.remove("sorce.html")
    await bot.send_photo(chat_id=-1001220184990, photo=photo, caption=text, parse_mode="HTML")


async def getLastBuildDate():
    wget.download("https://sourceforge.net/p/xiaomi-eu-multilang-miui-roms/activity/feed", "sorce.html")
    with open("sorce.html", "r") as f:
        index = f.read()
    soup = BeautifulSoup(index, "lxml")
    lastbuilddate = soup.find("lastbuilddate").text[0:-6]
    if lastbuilddate != worksheet.acell('G1').value:
        worksheet.update('G1', lastbuilddate)
        await post()
    else:
        os.remove("sorce.html")
    f.close()

@dp.message_handler(commands=['manual'])
async def manualPost(message: types.Message):
    if message.chat.id == -1001220184990:
        title = str(message.get_args())
        text = postText(title)
        photo = postPhoto(title)
        await bot.send_photo(chat_id="@xiaomieu_channel", photo=photo, caption=text, parse_mode="HTML")
        await bot.send_message(chat_id=message.chat.id, text="Готово!")

scheduler = AsyncIOScheduler()
scheduler.add_job(getLastBuildDate, "interval", seconds=10, start_date='2000-01-01 00:00:00')
scheduler.start()
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)