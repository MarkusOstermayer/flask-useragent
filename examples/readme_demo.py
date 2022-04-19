from flask import request
from flask import Flask
from flask_useragent import FlaskUserAgent


app = Flask(__name__)
ua_app = FlaskUserAgent(app)


# This should match user-agents used by curl
@ua_app.ua_route("/", user_agent=r"curl\/[0-9.]+")
def curl_endpoint():
    return "you use curl"


# This should match user-agents used by Mozilla Firefox
@ua_app.ua_route("/", user_agent="Mozilla[.a-zA-Z0-9/ ();_:]+")
def firefox_endpoint():
    return "you used a firefox based browser"


# This function is used as a fallback function in case either curl nor
# Firefox is being used
@ua_app.fallback("/")
def fallback_endpoint():
    user_agent = request.headers.get("User-Agent")
    return f"{user_agent}"


if __name__ == "__main__":
    app.run(debug=True)
