from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, QuickReplyButton, MessageAction, QuickReply,ImageSendMessage, VideoSendMessage, StickerSendMessage, AudioSendMessage
)
import os
import random
from time import time
from datetime import timedelta

app = Flask(__name__)

#環境変数取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

lesson = {
    '月曜日の時間割':'月曜日は\n1:こくご\n2:たいいく\n3:さんすう\nです。',
    '火曜日の時間割':'火曜日は\n1~2:りかじっけん\n3:こくご\nです。',
    '水曜日の時間割':'水曜日は\n1:さんすう\n2:おんがく\n3:せいかつ\nです。',
    '木曜日の時間割':'木曜日は\n1:たいいく\n2:かていか\n3:りか\nです。',
    '金曜日の時間割':'金曜日は\n1:さんすう\n2:こくご\n3:がっかつ\nです。'
}

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

user = {}
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    id = event.source.user_id   #LINEのユーザーIDの取得

    # 時間割言うやつ
    if event.message.text =='時間割を教えて':
        day_list = ["月", "火", "水", "木", "金"]
        items = [QuickReplyButton(action=MessageAction(label=f"{day}", text=f"{day}曜日の時間割")) for day in day_list]
        messages = TextSendMessage(text="何曜日の時間割ですか？",quick_reply=QuickReply(items=items))
        line_bot_api.reply_message(event.reply_token, messages=messages)
    elif event.message.text in lesson:
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=lesson[event.message.text])
        )

    # オウム返し
    elif event.message.text == 'オウム返し':
        message = event.message.text
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

    # Timer
    elif event.message.text == "start":

        if not id in user:  #新規ユーザーの場合
            user[id] = {}
            user[id]["total"] = 0

        user[id]["start"] = time()  #start実行時の時間を取得

        totalTimeStr = timedelta(seconds = user[id]["total"])  #s -> h:m:s

        reply_message = f"Start Timer\n\nTotal: {totalTimeStr}"

    elif event.message.text == "stop":
        end = time()  #end実行時の時間を取得
        dif = int(end - user[id]["start"])  #経過時間を取得
        user[id]["total"] += dif  #総時間を更新

        timeStr = timedelta(seconds = dif)
        totalTimeStr = timedelta(seconds = user[id]["total"])

        reply_message = f"Stop Timer\n\nTime: {timeStr}s\nTotal: {totalTimeStr}"

    elif event.message.text == "reset":
        user[id]["total"] = 0 #総時間を0にリセット

        totalTimeStr = timedelta(seconds = user[id]["total"])

        reply_message = f"Reset Timer\n\nTotal: {totalTimeStr}"

    else:
        reply_message = "Please send \"start\" or \"stop\"or \"reset\""  #指定外の3語に対する応答

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
