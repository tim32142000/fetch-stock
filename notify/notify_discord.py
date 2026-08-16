import os
import requests

webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
message = "台積電(2330.TW) 股價已更新"  # 之後可讀取你的摘要檔案內容

response = requests.post(webhook_url, json={"content": message})
response.raise_for_status()
print("Discord 通知已送出")