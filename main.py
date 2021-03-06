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
import requests
import json

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

# TimeTree API
ACCESS_TOKEN = 'EDR9y9hK7VVVU98P4WPXN6PyIhXEj1qmv6uspNCEy8Har2Ee'

# ヘッダーの設定
headers = {'Accept': 'application/vnd.timetree.v1+json',
'Authorization': 'Bearer ' + ACCESS_TOKEN}

URL_CIRCLE = 'https://timetreeapis.com/calendars/KppFAdQn8Rfm/upcoming_events?timezone=Asia/Tokyo'
URL_MY = 'https://timetreeapis.com/calendars/xWZ6gorhZDAD/upcoming_events?timezone=Asia/Tokyo'
URL_FAM = 'https://timetreeapis.com/calendars/n2htotVABDVf/upcoming_events?timezone=Asia/Tokyo'

r = requests.get(URL_CIRCLE, headers=headers)
data_cir = r.json()
r = requests.get(URL_MY, headers=headers)
data_my = r.json()
r = requests.get(URL_FAM, headers=headers)
data_fam = r.json()


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

    # 時間割言うやつ---------------------------------
    if event.message.text =='時間割':
        day_list = ["月", "火", "水", "木", "金"]
        items = [QuickReplyButton(action=MessageAction(label=f"{day}", text=f"{day}曜日の時間割")) for day in day_list]
        messages = TextSendMessage(text="何曜日の時間割ですか？",quick_reply=QuickReply(items=items))
        line_bot_api.reply_message(event.reply_token, messages=messages)
    elif event.message.text in lesson:
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=lesson[event.message.text])
        )

    # オウム返し------------------------------------
    elif event.message.text == 'オウム返し':
        message = event.message.text
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

    # Calender 表示
    elif event.message.text == "カレンダー":
        message = "今日の予定!\n---------\n【My calender】\n"
        for event_my in data_my['data']:
            message += "・" + event_my['attributes']['title'] + "\n"
        message += "---------\n【軽音】\n"
        for event_cir in data_cir['data']:
            message += "・" + event_cir['attributes']['title'] + "\n"
        message += "---------\n【Family】\n"
        for event_fam in data_fam['data']:
            message += "・" + event_fam['attributes']['title'] + "\n"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    

    # Timer----------------------------------------
    elif event.message.text == "start":

        if not id in user:  #新規ユーザーの場合
            user[id] = {}
            user[id]["total"] = 0

        user[id]["start"] = time()  #start実行時の時間を取得

        totalTimeStr = timedelta(seconds = user[id]["total"])  #s -> h:m:s

        reply_message = f"Start Timer\n\nTotal: {totalTimeStr}"

        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message))

    elif event.message.text == "stop":
        end = time()  #end実行時の時間を取得
        dif = int(end - user[id]["start"])  #経過時間を取得
        user[id]["total"] += dif  #総時間を更新

        timeStr = timedelta(seconds = dif)
        totalTimeStr = timedelta(seconds = user[id]["total"])

        reply_message = f"Stop Timer\n\nTime: {timeStr}s\nTotal: {totalTimeStr}"

        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message))

    elif event.message.text == "reset":
        user[id]["total"] = 0 #総時間を0にリセット

        totalTimeStr = timedelta(seconds = user[id]["total"])

        reply_message = f"Reset Timer\n\nTotal: {totalTimeStr}"

        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message))

    elif event.message.text == "wordle":
        answer = 'reach'
        l_answer = list(answer)
        len_answer = len(l_answer)
        win = False

        for l in range(len_answer):
            reply_message = "Input 5 char: "
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
            @handler.add(MessageEvent, answer=TextMessage)
            def handle_message(event):
                word = event.message.text
                len_word = len(word)
                l_word = list(word)
    
                result = [0, 0, 0, 0, 0]
                len_result = len(result)
    
                if len_word != 5:
                    reply_message = "I said \"Input 5 char.\"\n"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
                elif answer == word:
                    reply_message = "Correct!!"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
                    break
                else:
                    for i in range(len_answer):
                        for j in range(len_word):
                            if l_answer[i] == l_word[i]:
                                result[i] = 2
                            elif l_answer[i] == l_word[j]:
                                result[j] = 1
                    reply_message = "challenge result\n"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
                    for k in range(len_result):
                        if result[k] == 0:
                            message += "✕ "
                        elif result[k] == 1:
                            message += "△ "
                        elif result[k] == 2:
                            message += "◯ "
                        else:
                            message += "error "
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        
                reply_message = "\nInput Next word.\n"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
    # else:
    #     reply_message = "Please send \"start\" or \"stop\"or \"reset\""  #指定外の3語に対する応答

    


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
