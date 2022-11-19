# source: https://stackoverflow.com/questions/63769685/discord-py-how-to-send-a-message-everyday-at-a-specific-time
import asyncio
from datetime import datetime, time, timedelta
from time import sleep

import discord
from bs4 import BeautifulSoup
from decouple import config
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

DISCORD_BOT_TOKEN = config("TOKEN")
CHANNEL_ID = config("CHANNEL_ID")
PROBLEM_UPDATE_TIME = time(10, 00, 0)

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def get_problem():
    options = Options()
    options.headless = True
    service = Service("./geckodriver")
    driver = webdriver.Firefox(service=service, options=options)
    driver.get("https://leetcode.com/problemset/all/")
    sleep(5)
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, "html.parser")
    problem_element = soup.find_all(role="row")[1].find_all("a")[1]
    return (problem_element.text, problem_element["href"])


async def send_problem_update():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    problem = get_problem()
    result = f"Today's leetcode question is: [{problem[0]}](https://leetcode.com{problem[1]})"
    print(result)
    # await channel.send(result)


async def background_task():
    now = datetime.utcnow()
    if now.time() > PROBLEM_UPDATE_TIME:
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()
        await asyncio.sleep(seconds)
    while True:
        now = datetime.now()
        target_time = datetime.combine(now.date(), PROBLEM_UPDATE_TIME)
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target)
        await send_problem_update()
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()
        await asyncio.sleep(seconds)


async def main():
    async with client:
        client.loop.create_task(background_task())
        await client.start(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
