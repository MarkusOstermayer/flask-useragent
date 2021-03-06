from flask import Flask
from flask import request
from flask_useragent import FlaskUserAgent

app = Flask(__name__)
ua_app = FlaskUserAgent(app)


@ua_app.ua_route("/", user_agent=r"curl\/[0-9.]+")
def curl_endpoint():
    return "you use curl"


@ua_app.ua_route("/", user_agent=r"curl/7.82.0")
def curl_endpoint1():
    return "you use curl 7.82.0"


@ua_app.ua_route("/", user_agent="Mozilla[.a-zA-Z0-9/ ();_:]+")
def firefox_endpoint():
    return "you used a firefox based browser"


@ua_app.fallback("/")
def fallback_endpoint():
    user_agent = request.headers.get("User-Agent")
    return f"{user_agent}"


if __name__ == "__main__":
    app.run(debug=True)
