from setuptools import setup

APP = ['main.py']  # 主脚本文件
DATA_FILES = []    # 如果有额外资源文件，可以在这里指定
OPTIONS = {
    'argv_emulation': True,
    'packages': [
        'googleapiclient',         # google-api-python-client
        'google.auth',              # google-auth
        'google_auth_oauthlib',     # google-auth-oauthlib
        'google_auth_httplib2',     # google-auth-httplib2
    ],
    'plist': {
        'CFBundleName': 'MCGoogleSync',             # 应用程序名称
        'CFBundleDisplayName': 'MC Google Sync',    # 应用程序在Finder中的显示名称
        'CFBundleIdentifier': 'com.mcgooglesync.myapp',  # 应用程序唯一标识符（建议以域名格式）
        'CFBundleVersion': '1.0',                   # 应用程序版本
        'CFBundleShortVersionString': '1.0.0',      # 简短版本号
        'CFBundleIconFile': 'AppIcon.icns',         # 应用程序图标文件（需是.icns格式）
    },
    'iconfile': 'AppIcon.icns'  # 图标文件路径 (.icns格式)
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
