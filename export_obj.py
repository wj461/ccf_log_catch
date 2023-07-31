import json
import time
import re
import os
import sys

from datetime import datetime


class ExportObj:
    def __init__(self, log_title, channel_list):
        self.dice_true_count = 0
        self.dice_false_count = 0

        self.write_head(log_title)
        self.write_button(log_title, channel_list)

        json_data = ''
        with open('log_data.json', 'r', encoding='UTF-8') as f:
            json_data = json.load(f)

        with open(f'{log_title}.html', 'a', encoding="UTF-8") as f_w:
            for i in json_data:
                s = self.write_channel_name_time(
                    i, channel_list) + self.write_text(i) + '</p></div>'
                f_w.write(s)

        self.write_script(log_title, channel_list)

        print("Export over")
        print("骰子成功次數:", self.dice_true_count)
        print("骰子失敗次數:", self.dice_false_count)

    def write_head(self, log_title):
        with open(f'{log_title}.html', 'w', encoding="UTF-8") as f_w:
            with open("style_format.html", 'r', encoding="UTF-8") as f:
                f_w.write(f.read())

            s = f'''
                <title>{log_title}</title>
                </head>
                <body>
                    <div class="title">{log_title}</div>
                    <hr>
            '''
            f_w.write(s)

    def write_button(self, log_title, channel_list):
        with open(f'{log_title}.html', 'a', encoding="UTF-8") as f_w:
            f_w.write(f'<nav>')
            for index, value in enumerate(channel_list):
                f_w.write(
                    f'<button class="channel_{index}_b">{value}</button>')
            f_w.write(f'''
            <label class="switch">
                <input type="checkbox">
                <span class="slider round"></span>
            </label>
            </nav>''')

    def write_channel_name_time(self, i, channel_list):
        date, time = i['createdAt'].split('T')
        time = f'{date} {time[:8]}'
        img = i['iconUrl']
        color = i['color']
        channel = i['channel']
        name = i['name']
        channel_id = channel_list.index(channel)
        channel_class = f"channel_{channel_id}"
        other = ''

        if channel_list.index(channel) == 2:
            other = '<span class="channel_2_block"></span>'

        s = f'''
            <div class= "{channel_class} content">
                {other}
                <div class="pic offset" style="float:left;"><img
                        src={img}>
                </div>
                <p style="color:{color};">
                <span> [{channel}]</span>
                <span>{name}</span> <span>- {time}</span>
        '''
        return s

    def write_text(self, i):
        span = '<span>'
        br_text = i['text'].replace('\n', '<br>')

        if re.findall('成功', i['result']) or re.findall('特殊', i['result']):

            span = '<span style="color:#2292eb">&#127922;'
            self.dice_true_count += 1
        elif re.findall('失败', i['result']) or re.findall('失敗', i['result']):
            span = '<span style="color:#F50057">&#127922;'
            self.dice_false_count += 1
        elif i['result'] != "":
            span = '<span>&#127922;'

        if i['secret']:
            text = f"{br_text}(secret)<br>{i['result']}"
        else:
            text = f"{br_text}<br>{i['result']}"

        s = f'''
            {span}
                    {text}
            </span>
        '''
        return s

    def write_script(self, log_title, channel_list):
        with open(f'{log_title}.html', 'a', encoding="UTF-8") as f_w:
            f_w.write(f'''<script> 
                var elements_arr = []
                var button_arr = []
            ''')
            for index, value in enumerate(channel_list):
                s = f'''
                var b_{index} = document.querySelector(".channel_{index}_b");
                var elements_{index} = document.querySelectorAll(".channel_{index}");
                elements_arr.push(elements_{index});
                button_arr.push(b_{index});
                '''
                f_w.write(s)

            with open("script.txt", 'r', encoding="UTF-8") as f:
                f_w.write(f.read())
