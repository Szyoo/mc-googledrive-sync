import json
import os
import logging

CONFIG_FILE = 'config/config.json'

def load_config():
    logging.info('加载配置文件')
    # 确保 config 目录存在
    if not os.path.exists(os.path.dirname(CONFIG_FILE)):
        os.makedirs(os.path.dirname(CONFIG_FILE))
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    logging.info('保存配置中')
    # 确保 config 目录存在
    if not os.path.exists(os.path.dirname(CONFIG_FILE)):
        os.makedirs(os.path.dirname(CONFIG_FILE))
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
