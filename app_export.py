import asyncio
import time
import os
import re
import json
import sys
import nest_asyncio

from datetime import datetime
from pyppeteer import launch

from json_obj import JsonObj
from export_obj import ExportObj

google_chrome_path = ".\\GoogleChromePortable\\GoogleChromePortable"
ban_check = ["Cthulhu", "Secret dice", "<"]
head_count_max = 1000
head_str = []
close_sign = False
busy_sign = False
busy_main_sign = False
page_up_done = False
nest_asyncio.apply()


async def while_pageUp(page):
    global head_str
    global close_sign
    global page_up_done

    last_head_str = ""
    head_str = []
    head_str_current = ""
    same_time = 0
    page_up_count = 0
    channel_index = -1
    page_up_done = False

    channel_list = await page.evaluate('() => [...document.querySelectorAll("button.sc-bhVIhj.jvHhUq")].map((e) => e.textContent).slice(0, -1)')
    for index, value in enumerate(channel_list):
        print(f'{index}. {value}')

    while (channel_index >= len(channel_list) or channel_index < 0):
        try:
            channel_index = int(input("input target channel index : "))
        except:
            channel_index = -1
            print("Please enter a valid number.")

    await page.evaluate(
        f'() => document.querySelectorAll("button.sc-bhVIhj.jvHhUq").forEach((e) =>{{ if (e.textContent == "{channel_list[channel_index]}")  e.click() }})'
    )

    await asyncio.sleep(3)

    while (same_time < head_count_max):
        await page.evaluate('document.querySelector(".sc-caXVBt > ul > div > div").scrollTop = 0')

        try:
            value = await page.evaluate('() => document.querySelector("p.MuiTypography-displayBlock").textContent')
        except:
            print("Catch channel head text false.")
            print("Maybe the channel is Empty.")
            close_sign = True
            return

        if value == last_head_str:
            same_time += 1
        else:
            same_time = 0

        last_head_str = value

        if ('\r' in last_head_str):
            continue
        head_str_current = f'"{last_head_str}"'.replace('\n', r'\\n')

        if (page_up_count % 2000 == 0):
            head = handle_head(head_str_current)
            if head != "":
                head_str.append(head)

        page_up_count += 1

    page_up_done = True
    print("PageUp channel done.")


def handle_head(head_str_current):
    head = re.sub("\s\([^)]+\)\s＞\s.*", "", head_str_current)
    head = re.sub("[()+\?{}|^$*]", ".", head)
    head = re.sub("\s?\[[^]]+\]", ".*?", head)

    if not (head in head_str) and not ("<" in head) and not ("Secret" in head):
        # print(f'text : {head}')
        return head
    return ""


async def handle_response(response):
    global close_sign
    global busy_sign

    # if busy_main_sign:
    #     return

    busy_sign = True
    if response.url.find("TYPE=xmlhttp") != -1:
        print('Catch TYPE = xmlhttp...')
        print(f'response.url = {response.url}')
        try:
            resp = await response.text()
        except:
            print("Response no text found.")
            return

        print(f'response.url = {response.url}')
        write_log(resp)
        close_sign = catch_head_str_from_log()

    busy_sign = False


def write_log(data):
    print('Write Log...')

    with open('log.txt', 'a', encoding='UTF-8') as f:
        f.write(data)


def catch_head_str_from_log():
    global head_str

    if not page_up_done:
        return False

    print("Catch head log")

    for text in head_str:
        with open("log.txt", 'r', encoding='UTF-8') as f:
            # print(f"Now text: {text}")
            trim = re.findall(text, f.read(), re.DOTALL)
            if len(trim) > 0:
                head_str.remove(text)
                print(f'page text : {trim[0]}')
                print("Find text from log.txt.")
            else:
                print("Find false.")
                return False
    return True


async def main():
    global close_sign
    global busy_main_sign

    browser = await launch(
        devtools=True,
        executablePath=google_chrome_path,
        args=['--disable-infobars']
    )
    # devtools true auto open chrome and F12

    url = input("Enter ccf room url: ")

    print('Catch WEB...')
    if (os.path.exists("log.txt")):
        os.remove("log.txt")
        print('REMOVE LOG.TXT')

    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()

    await page.evaluateOnNewDocument(
        'Object.defineProperty(navigator, "webdriver", \
        {get: () => undefined})')
    # 繞過擋webdriver的一些網站用

    await page.goto(url)

    page.on('response', lambda response: asyncio.ensure_future(
        handle_response(response)))
    # get response

    await page.waitForSelector(".MuiDialogContent-root")
    await page.click(".MuiDialogActions-spacing > button")  # cancel ad
    await asyncio.sleep(1)

    await while_pageUp(page)
    while (True):
        if not close_sign:
            await asyncio.sleep(10)
            continue

        if input("Continue? (y/N) : ").lower() != 'y':

            break

        close_sign = False
        await while_pageUp(page)

    print("close page")
    await page.close()
    print("close browser")
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())

json_obj = JsonObj()
ExportObj(json_obj.get_log_title(), json_obj.get_channel_list())

sys.exit()
