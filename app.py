from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from utils import fetch_reply

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/sms", methods=['POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    print(request.form)
    msg = request.form.get('Body')
    sender = request.form.get('From')
    
    # Create reply
    resp = MessagingResponse()
    reply_data,msg,type_image=fetch_reply(msg,sender)
    if type_image=="image":
        print(reply_data)
        resp.message(reply_data).media(msg)
    else:
        print(reply_data)
        resp.message(reply_data)
    #resp.message("You said: {}".format(msg))
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)