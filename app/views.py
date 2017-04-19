from app import app
from flask import request

@app.route('/')
@app.route('/index')
def index():
    return "HI world for the slack Bot"
    # return render_template('index.html', posts=posts, user=user)


@app.route('/slackhook', methods=['POST', 'GET'])
def slackmethod():
    print(request)
    return "Message from slack"


def getActionFromWebhook(request):
    return request.json["result"]["action"]
