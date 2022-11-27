import os

from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram import Bot, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import config
from aiogram.types import InputFile
from bs4 import BeautifulSoup
import wget, lxml
import gspread

worksheet = gspread.service_account(filename='level-slate-280111-4930953f5702.json').open_by_url('https://docs.google.com/spreadsheets/d/1m2O23ai-s83iNdPOOn4cLtHwc5Ciw82-RJvwW2gIvrk/edit#gid=0').get_worksheet(0)
bot = Bot(token=config.TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)


async def post():
    with open("sorce.html", "r") as f:
        index = f.read()
    soup = BeautifulSoup(index, "lxml")
    title = soup.find("item").find("title").text
    if "STABLE" in title:
        type = "STABLE"
        posttext = '<a href="https://t.me/xiaomieu_channel">channel</a> | <a href="https://t.me/xiaomieu_chat">chat</a> | #stable'
        photo = InputFile('files/stable_build.jpg')
    else:
        type = "WEEKLY"
        posttext = '<a href="https://t.me/xiaomieu_channel">channel</a> | <a href="https://t.me/xiaomieu_chat">chat</a> | #weekly'
        photo = InputFile('files/weekly_build.jpg')

    y = title.find('V')
    if "fastboot" in title:
        version = title[y:-28]
    else:
        version = title[y:-19]
    while (True):
        x = 2
        if str(worksheet.acell(f'A{x}').value) in title:
            name = worksheet.acell(f'B{x}').value
            break
        x = x + 1

    link = "https://sourceforge.net/projects/xiaomi-eu-multilang-miui-roms/files" + title[39:] + "/download"

    text = f"Обновление {type} | {version} доступно для {name}\n\n{link}\n\n{posttext}"
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


scheduler = AsyncIOScheduler()
scheduler.add_job(getLastBuildDate, "interval", seconds=10, start_date='2000-01-01 00:00:00')
scheduler.start()
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)