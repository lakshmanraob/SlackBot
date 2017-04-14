from app import app
from flask import render_template, redirect, url_for, request, abort

from app.static import myfirebasemodule
from app.static import climatemodule

from app.static import gihubmodule
from app.static import mycirclecimodule
from app.static import jiramodule

import json
import requests
from flask import jsonify

global sessionId
apiKey = 'd659ec8acdd44141b7c7edddc555618a'

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'lakshman'}

    posts = [
        {
            'author': {'nickname': 'lakshman'},
            'body': 'Beautiful day in India'
        },
        {
            'author': {'nickname': 'madhu'},
            'body': 'Good man'
        },
        {
            'author': {'nickname': 'anoop'},
            'body': 'Quality Assurance'
        }
    ]
    myfirebase = myfirebasemodule.myfirebase()
    # myfirebase.accessFirebase()

    return render_template('index.html', posts=posts, user=user)


def checkFun():
    return "check functionality"


# Another way of routing
app.add_url_rule('/check', 'checkStr', checkFun)


@app.route("/admin")
def iamAdmin():
    return "hi Admin"


# argument passing
@app.route('/hi/<name>')
def checkName(name):
    if name == 'admin':
        return redirect(url_for('iamAdmin'))
    else:
        return "hello %s!" % name


@app.route('/square/<int:postId>')
def square(postId):
    return str(postId * postId)


@app.route('/rev/<float:revNo>')
def revNumber(revNo):
    return str(revNo)


@app.route('/login', methods=['POST', 'GET'])
def loginAccount():
    if request.method == 'POST':
        user = request.form['nm']
        return 'POST method..' + user
    else:
        user = request.args.get('nm')
        return 'GET method..' + user


@app.route('/webhook', methods=['POST', 'GET'])
def webhookExp():
    webhookaction = getActionFromWebhook(request=request)
    if webhookaction in ['weather.search', 'wind.search']:
        climateaction = climatemodule.climateaction()
        if request.method == 'POST':
            location = climateaction.getLocation(req=request)
            if location:
                print("weather condition required for ..", location)
                return climateaction.processAction(request)
            else:
                print("actual json file", request.json)
        elif request.method == 'GET':
            return climateaction.processGetrequest(request)
        else:
            abort(400)
    elif webhookaction in ['firebase.action', 'firebase.status.action']:
        return processFirebaseRequests(request=request)
    else:
        abort(400)


@app.route('/firebase', methods=['POST', 'GET'])
def firebaseapp():
    return processFirebaseRequests(request=request)


@app.route('/github', methods=['POST', 'GET'])
def accessGithub():
    print("git hub access")
    github = gihubmodule.githubexp()
    # return github.authenticateWithToken()
    results = github.getcommitsforDev(maxresults=10)
    print(results)
    return processGitCommitDetails(results)


@app.route('/circleci', methods=['POST', 'GET'])
def accesscircleci(sessionId):
    '''For triggering the build in the circle CI'''
    print("access circle ci")
    circle = mycirclecimodule.mycircleclient()
    triggerBuild = circle.triggerbuild()
    speech = "build intiated.."
    return buildResponse(speech=speech, displayText=speech, source="lakshman web hook", contextOut=None,
                         responseCode=200)


@app.route('/jiraissues', methods=['POST', 'GET'])
def getJiraIssues():
    jiraclient = jiramodule.myjiraclient()
    # for jiraIssue in jiraclient.getCurrentUserIssues(maxResults=10):
    #     print(jiraclient.getIssuedetails(jiraIssue).fields.summary)
    results = jiraclient.getCurrentUserIssues(maxResults=10)
    return buildResponse(speech=results, displayText=results, contextOut=None, source="lakshman web hook",
                         responseCode=200)


@app.route('/buildhook', methods=['POST', 'GET'])
def handlebuildDetails():
    try:
        if request.json["payload"]:
            return cipostaccept()
    except KeyError as e:
        buildaction = getActionFromWebhook(request=request)
        if buildaction == "gitdetails.action":
            return accessGithub()
        elif buildaction == 'jiradetails.action':
            return getJiraIssues()
        elif buildaction == 'ci.action':
            global sessionId
            sessionId = request.json["sessionId"]
            return accesscircleci(sessionId)
        return buildaction


@app.route('/cipostaccept', methods=['POST', 'GET'])
def cipostaccept():
    print('this request came')
    print(sessionId)
    print(request.json["payload"]["outcome"])
    print(request.json["payload"]["username"])
    print(request.json["payload"]["committer_date"])
    apiUrl = 'https://api.api.ai/api/query?v=20150910'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer %s' % apiKey,
    }

    if request.json["payload"]["outcome"] == "success":
        circle = mycirclecimodule.mycircleclient()
        user = request.json["payload"]["username"]
        project = request.json["payload"]["reponame"]
        buildnum = request.json["payload"]["build_num"]
        data = '{\'event\':{ \'name\': \'buildresponse\', \'data\': {\'result\': \'success\'}}, \'timezone\':\'America/New_York\', \'lang\':\'en\', \'sessionId\':\'%s\'}' % sessionId

        followupevent = '{ \'name\': \'buildresponse\', \'data\': {\'result\': \'success\'}}'
        # ', \'timezone\':\'America/New_York\', \'lang\':\'en\', \'sessionId\':\'%s\'}' % sessionId
        artifacts = circle.getartifactslist(user=user, project=project, buildnumber=buildnum)
        artifactsList = []
        for arti in artifacts:
            str = arti['url']
            artifactsList.append(str)
        response = requests.post('https://api.api.ai/api/query?v=20150910', headers=headers, data=data)
        print(response.content.decode("utf-8"))
        # return "success"
        return buildResponse(speech=artifactsList, displayText=artifactsList, source="lakshman webhook",
                             contextOut=None, followupevent=followupevent, responseCode=200)
        # return json.dumps(artifactsList)
    else:
        speech = "fail to get the artifacts"
        return buildResponse(speech=speech, displayText=speech, source="lakshman webhook",
                             contextOut=None, responseCode=400)


def getActionFromWebhook(request):
    return request.json["result"]["action"]


def processFirebaseRequests(request):
    firebaseapp = myfirebasemodule.myfirebase()
    if request.method == 'POST':
        print(request.json)
        action = request.json["result"]["action"]
        username = request.json["result"]["parameters"]["username"]
        password = request.json["result"]["parameters"]["password"]
        if username == None:
            username = request.form('username')
        if password == None:
            password = request.form('password')
        if action == 'firebase.action':
            loginInfo = firebaseapp.loginFirebase(email=username, password=password)
            result = json.loads(loginInfo)
            # here we are not sending the User object as response
            return buildResponse(speech=result['status'], displayText=result['status'], source='lak webhook',
                                 contextOut=None,
                                 responseCode=result['responsecode'])
        elif action == 'firebase.status.action':
            item = request.json["result"]["parameters"]["deviceorbook"]
            statusInfo = firebaseapp.accessDatabase(email=username, password=password, item=item)
            result = json.loads(statusInfo)
            # here we are not sending the User object as response
            return buildResponse(speech=result['status'], displayText=result['status'], source='lak webhook',
                                 contextOut=None,
                                 responseCode=result['responsecode'])
        else:
            str = 'Not able recognize the request'
            return buildResponse(speech=str, displayText=str, source='laksh webhook', contextOut=None, responseCode=400)

    else:
        print("GET Method ", request.args.get("nm"))
        # method = "GET Method " + request.args.get("nm")
        username = request.args.get("username")
        password = request.args.get("password")
        print("username" + username + ",password." + password)
        createUserInfo = firebaseapp.createUser(username=username, password=password)
        result = json.loads(createUserInfo)
        # here we are not sending the User object as response
        return buildResponse(speech=result['status'], displayText=result['status'], source='lak webhook',
                             contextOut=result['user'], responseCode=result['responsecode'])


def processGitCommitDetails(jsonresult):
    speech = jsonresult
    # for sp in speech:
    #     print(sp)
    return buildResponse(speech=speech, displayText=speech, source="lakshman webhook", contextOut=None,
                         responseCode=200)

    # return buildGitResponse(speech=None, displayText=None, source=None, contextOut=None, responseCode=200)


def getProperty(request, attributeName):
    return request.json["result"][attributeName]


def buildGitResponse(speech, displayText, source, contextOut, responseCode):
    messages = '[{"type":0,"speech":"message1"},{"type":0,"speech":"message2"},{"type":0,"speech":"message3"},{"imageUrl":"https://www.sencha.com/wp-content/uploads/2016/02/icon-sencha-test-cli.png","type":3}]'
    # return jsonify(
    #     {'speech': speech, 'displayText': displayText, 'source': source,
    #      'contextOut': contextOut, 'message': messages}), responseCode
    return jsonify(
        {'speech': "", 'displayText': "displaytext", 'source': "lakshman",
         'contextOut': None, 'message': messages}), responseCode


def buildResponse(speech, displayText, source, contextOut, responseCode):
    messages = '[{"type":0,"speech":"build server not able to serve your request"},{"imageUrl":"https://www.sencha.com/wp-content/uploads/2016/02/icon-sencha-test-cli.png","type":3}]'
    # return jsonify(
    #     {'speech': speech, 'displayText': displayText, 'source': source,
    #      'contextOut': contextOut, 'message': messages}), responseCode
    return jsonify(
        {'speech': speech, 'displayText': displayText, 'source': source,
         'contextOut': contextOut}), responseCode


def buildResponse(speech, displayText, source, contextOut, responseCode, followupevent):
    return jsonify(
        {'speech': speech, 'displayText': displayText, 'source': source,
         'contextOut': contextOut, 'followupEvent': followupevent}), responseCode
