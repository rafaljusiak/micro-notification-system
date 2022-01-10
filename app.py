import os
import slack
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
from jira import JIRA

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route("/", methods=["POST"])
@cross_origin(origin="*")
def send():
    client = slack.WebClient(token=os.getenv("SLACK_API_TOKEN"))
    channel = os.getenv("SLACK_NOTIFICATIONS_CHANNEL")
    body = request.json.get("message")
    message = f"<!channel>\n\n:fire: *Użytkownik zgłosił problem:* :fire:\n\n {body}"
    client.chat_postMessage(channel=channel, text=message)

    state = request.json.get("state", None)
    if state:
        client.files_upload(channels=channel, content=state)

    jira = JIRA(
        server=os.getenv("JIRA_URL"),
        basic_auth=(
            os.getenv("JIRA_EMAIL"),
            os.getenv("JIRA_API_KEY"),
        ),
    )
    jira.create_issue(
        project=os.getenv("JIRA_PROJECT"),
        summary=body.replace("\n", " ")[:80] + "...",
        description=message,
        issuetype={"name": "Bug"},
    )

    return Response()
