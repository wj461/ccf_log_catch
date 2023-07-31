import json
import time
import re
import os
import sys

from datetime import datetime, timedelta


class JsonObj:
    def __init__(self):
        self.need_data_list = [
            ["text", "stringValue"],  # 文字內容
            ["type", "stringValue"],  # text
            ["extend", "mapValue", "fields", "roll", "mapValue",
                "fields", "result", "stringValue"],  # dice result
            ["extend", "mapValue", "fields", "roll", "mapValue",
                "fields", "secret", "booleanValue"],  # dice result
            ["createdAt", "timestampValue"],  # time
            ["channel", "stringValue"],  # channel
            ["color", "stringValue"],  # name color
            ["name", "stringValue"],  # char name
            ["iconUrl", "stringValue"]  # imageUrl
        ]

        self.read_json_name = "log_not_handle.json"
        self.download_file_name = "log.txt"
        self.dump_json_name = 'log_data.json'
        self.log_title = ''
        self.channel_list = ['main', 'info', 'other']

        json_data = ''
        result_list = []
        dump_json_name = 'log_data.json'

        self.clean_log()

        with open(self.read_json_name, 'r', encoding='UTF-8') as f:
            json_data = json.load(f)

        for target in json_data:
            for i in target:
                result = self.filter_talk(i)
                if result != None:
                    # print("time : ", result['createdAt'], result['timestamp'])
                    # print(result['text'], result['result'], result['channel'])
                    result_list.append(result)

        with open(dump_json_name, 'w', encoding='UTF-8') as f:
            sort_list = sorted(result_list, key=lambda d: d['timestamp'])
            print(f"Dump json file '{self.log_title}'")
            json.dump(sort_list, f, ensure_ascii=False)

        if (os.path.exists(self.read_json_name)):
            os.remove(self.read_json_name)
            print(f'REMOVE {self.read_json_name}.TXT')

    def clean_log(self):
        f_w = open(self.read_json_name, 'w', encoding='UTF-8')
        f_w.write('[')

        with open(self.download_file_name, 'r', encoding='UTF-8') as f:
            for line in f.readlines():
                if re.match(r'^\d', line):
                    continue
                data = re.sub(r'(?<=]]])\d+', ',', line)
                f_w.write(data)
                # print(f"{data = }")

        f_w.write(']')
        f_w.close()
        print("Clean log data over 'log_not_handle.json'")

    def filter_talk(self, target):
        current_dict = self.catch_fields_data(target)
        if current_dict == None:
            return
        # pprint(current_dict)
        # print()
        keys = list(current_dict.keys())
        if 'diceBotName' in keys:
            self.log_title = f"{current_dict['name']['stringValue']} - {current_dict['diceBotName']['stringValue']}"

            try:
                for i in current_dict['messageChannels']['arrayValue']['values']:
                    self.channel_list.append(i['stringValue'])
            except:
                pass

        if 'text' in keys:
            need_data = self.catch_need_data(current_dict)
            return need_data

    def catch_fields_data(self, target):
        dict_data = {}
        for data in target:
            try:
                dict_data = (data[0]['documentChange']['document']['fields'])
                return dict_data
            except:
                pass

    def catch_need_data(self, target):
        data_dict = {}
        for keys in self.need_data_list:
            value = self.catch_data_by_keys(target, keys)
            data_dict[keys[-2]] = value

        data_dict['createdAt'] = self.change_time_zone(data_dict['createdAt'])
        data_dict['timestamp'] = self.datetime_to_timestamp(
            data_dict['createdAt'])

        return data_dict

    def catch_data_by_keys(self, target, keys):
        temp = target
        for key in keys:
            try:
                temp = temp[key]
            except:
                temp = ""
                break

        return temp

    def datetime_to_timestamp(self, time_str):
        timestamp = 0
        try:
            timestamp = time.mktime(datetime.strptime(
                time_str, "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())*1000 + int(time_str[-4:-1])
        except:
            timestamp = time.mktime(datetime.strptime(
                time_str, "%Y-%m-%dT%H:%M:%SZ").timetuple())*1000

        return timestamp

    def change_time_zone(self, time_str):
        day, time = time_str.split("T")
        y, m, d = day.split("-")
        hour, minute, sec = time.split(":")
        temp_time = f"{y}-{m}-{d}T{hour}:{minute}"

        day1 = datetime.strptime(temp_time, '%Y-%m-%dT%H:%M')
        day1 += timedelta(hours=8)
        return datetime.strftime(day1, '%Y-%m-%dT%H:%M:%S')[:-2]+sec

    def get_log_title(self):
        return self.log_title

    def get_channel_list(self):
        return self.channel_list
