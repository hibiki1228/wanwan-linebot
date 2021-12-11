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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
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
        rep = TextSendMessage(text="なにかしゃべって！")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=rep))

        message = event.message.text
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
