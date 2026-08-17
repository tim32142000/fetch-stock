import os
import requests

token = os.environ["LINE_CHANNEL_TOKEN"]
user_id = os.environ["LINE_USER_ID"]
message = "台積電(2330.TW) 今日收盤: 950 (+1.2%)"

url = "https://api.line.me/v2/bot/message/push"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}
payload = {
    "to": user_id,
    "messages": [{"type": "text", "text": message}],
}

response = requests.post(url, headers=headers, json=payload)
response.raise_for_status()
print("LINE 通知已送出")