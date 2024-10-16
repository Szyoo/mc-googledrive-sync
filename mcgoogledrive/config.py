import json
import os
import logging

CONFIG_FILE = 'config/config.json'

def load_config():
    logging.info('加载配置文件')
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    logging.info('保存配置中')
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
