from app import app
from flask import request
import json


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


def getActionFromWebhook(request):
    return request.json["result"]["action"]
