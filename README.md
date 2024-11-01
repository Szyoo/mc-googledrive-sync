# mc-googledrive-sync

Synchronize the mods and saves folder with Google Drive

### 创建虚拟环境：

```bash
python3 -m venv .venv/
```

### 激活虚拟环境：

```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate  # Windows
```

### 安装依赖：

```bash
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 py2app
pip install --upgrade pip
python3 --version
## 在@后面输入刚刚获得的前两部分大版本号，比如 3.12.7 则输入 @3.12
brew install python-tk@
```

### 打包:

```bash
pyinstaller --onefile --windowed main.py
cp -R dist/main.app /Applications/
mv /Applications/main.app /Application/MC-Google-Sync
```
