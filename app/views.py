from app import app
from flask import request, Response, make_response
import json
from slackclient import SlackClient

SLACK_BOT_TOKEN = 'xoxb-171288352757-ZHEdu1wAG9xpebMiDlbIbqwh'

slack_client = SlackClient(SLACK_BOT_TOKEN)


@app.route('/')
@app.route('/index')
def index():
    return "HI world for the slack Bot"
    # return render_template('index.html', posts=posts, user=user)


@app.route('/slackhook', methods=['POST', 'GET'])
def slackmethod():
    print(request.form["payload"])
    form_json = json.loads(request.form["payload"])
    print(form_json)
    return "Message from slack"


@app.route("/slack/message_options", methods=["POST"])
def message_options():
    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    menu_options = {
        "options": [
            {
                "text": "Chess",
                "value": "chess"
            },
            {
                "text": "Global Thermonuclear War",
                "value": "war"
            }
        ]
    }

    return Response(json.dumps(menu_options), mimetype='application/json')


@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    print("Are we getting the request here")
    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    # Check to see what the user's selection was and update the message
    # selection = form_json["actions"][0]["selected_options"][0]["value"]

    selection = form_json["actions"][0]["value"]

    if selection == "yes":
        message_text = "@"+form_json["user"]["name"] + " responded " + selection + " for " + \
                       form_json["original_message"]["attachments"][0]["text"]
    else:
        message_text = "NO questiion to display"

    # if selection == "war":
    #     message_text = "The only winning move is not to play.\nHow about a nice game of chess?"
    # else:
    #     message_text = ":horse:"

    response = slack_client.api_call(
        "chat.update",
        channel=form_json["channel"]["id"],
        ts=form_json["message_ts"],
        text=message_text,
        attachments=[]
    )

    return make_response("", 200)


def getActionFromWebhook(request):
    return request.json["result"]["action"]
