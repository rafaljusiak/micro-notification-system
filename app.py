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

    content = request.json.get("content")
    email = request.json.get("email")
    type = request.json.get("type")
    message = request.json.get("message")

    slack_message = f"<!channel>\n\n:fire: *Użytkownik zgłosił problem:* :fire:\n\n {message}"
    client.chat_postMessage(channel=channel, text=slack_message)

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

    if content is not None:
        email_response_example = f"""Dziękuję za zgłoszenie
        
    {message}
    
    Pozdrawiam,
    Michał z Zespołu Moja Matura
    """

        jira.create_issue(
            project=os.getenv("JIRA_PROJECT"),
            summary=f"[{type}][{email}]: " + content.replace("\n", " "),
            description=f"Użytkownik: {email}" + "\n\n" + email_response_example,
            issuetype={"name": "Bug"},
        )
    else:
        email_response_example = f"""Dziękuję za zgłoszenie
        
    kategoria: {type}
    opis: {message}
    
    Pozdrawiam,
    Michał z Zespołu Moja Matura
    """

        jira.create_issue(
            project=os.getenv("JIRA_PROJECT"),
            summary=message.replace("\n", " ")[:80] + "...",
            description=f"Użytkownik: {email}" + "\n\n" + email_response_example,
            issuetype={"name": "Bug"},
        )

    return Response()
