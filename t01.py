"""
將 Todoist 明天前的任務同步到 Habitica，用來自動刷等@@
"""

from pytodoist import todoist
from datetime import datetime, timedelta
import json
import requests
import yaml
import os


class habitica:
    def __init__(self, user, key):
        self.user = user
        self.key = key
        self.auth = {'x-api-user': self.user, 'x-api-key': self.key}

    def add_todo_task(self, task, priority=None, date=None):
        data = {"text": task, "type": 'todo'}
        if priority:
            data['priority'] = priority
        if date:
            data['date'] = date

        url = 'https://habitica.com/api/v3/tasks/user'
        r = requests.post(url, data=data, headers=self.auth)
        json_b = r.content
        print(json.dumps(json.loads(json_b), indent=4, sort_keys=True))


def load_account_data(yaml_filepath):
    with open(yaml_filepath, 'r') as f:
        account_data = yaml.load(f)
        return account_data


def date_compare(data1, data2):
    if data2.year > data1.year:
        return True
    elif data2.year < data1.year:
        return False
    else:
        if data2.month > data1.month:
            return True
        elif data2.month < data1.month:
            return False
        else:
            if data2.day >= data1.day:
                return True
            else:
                return False


account_file = input('account file path: ') or 'account.yaml'

if not os.path.exists(account_file):
    with open('account.yaml', 'w') as f:
        data_dict = {'todoist': {'email': '', 'password': ''}, 'habitica': {'user': '', 'key': ''}}
        yaml.dump(data_dict, f, default_flow_style=False)
    print('please input your account in account.yaml')
else:
    account_data = load_account_data(account_file)
    habitica_user = habitica(account_data['habitica']['user'], account_data['habitica']['key'])
    user = todoist.login(account_data['todoist']['email'], account_data['todoist']['password'])
    print('login Todoist')
    tasks = user.get_tasks()
    print('get todoist tasks')

    tomorrow = datetime.now() + timedelta(days=1)
    for task in tasks:
        t_priority = task.priority

        if t_priority == 4:
            h_priority = 2
        elif t_priority == 3:
            h_priority = 1.5
        else:
            h_priority = 1

        if task.due_date_utc:
            cday = datetime.strptime(task.due_date_utc, '%a %d %b %Y %H:%M:%S %z')
            if date_compare(cday, tomorrow):
                habitica_user.add_todo_task('[T]' + task.content, h_priority, task.due_date_utc)
