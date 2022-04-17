flask-useragent
===============

flask-useragent gives one the ability to create functions, that are only
triggered by flask if the URL and the useragent matches.

Why does it exist?
------------------

This project was inspired by [this twitterthread](https://twitter.com/thomasfricke/status/1373927911561043971).
It is just a funny sideproject, please don't use this project in
any serious environment.

The task can be easily solved with the following code:
~~~python
from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/")
def main_page():
    user_agent = request.headers.get("User-Agent")

    if "curl" in user_agent:
        return "you used curl"

    if "Mozilla" in user_agent:
        return "you used a firefox based browser"

    return f"{user_agent}"


if __name__ == "__main__":
    app.run(debug=True)
~~~

However, while solving this task, I wondered if it would be possible to solve
it with the ```route()```-Decorator which lead me to write flask-useragent.

With it, the above example can be written as:

~~~python
from flask_useragent import Flask
from flask import request

app = Flask(__name__)


# This should match user-agents used by curl
@app.ua_route("/", user_agent=r"curl\/[0-9.]+")
def curl_endpoint():
    return "you use curl"


# This should match user-agents used by Mozilla Firefox
@app.ua_route("/", user_agent="Mozilla[.a-zA-Z0-9/ ();_:]+")
def firefox_endpoint():
    return "you used a firefox based browser"


# This function is used as a fallback function in case either curl nor
# Firefox is being used
@app.fallback("/")
def fallback_endpoint():
    user_agent = request.headers.get("User-Agent")
    return f"{user_agent}"


if __name__ == "__main__":
    app.run(debug=True)

~~~

Usage
-----
-----

flask-useragent works just like flask, except that it provides two new
Functiondecorator.

### ua_route

This Decorator can be used to restrict the underlying function to
a certain user-agent. It expects a keyword_argument called ```user_agent```.
The provided string can be a regex expression or a full user-agent-string.

If there are a regex-string that would match and a exact one, the exact one
will be used.

The following example shows how to use the ua_route Decorator
~~~python
from flask_useragent import Flask
from flask import request

app = Flask(__name__)

# This uses a specific user-agent-string 
@app.ua_route("/", user_agent=r"curl/7.82.0")
def curl_endpoint_7_82_0():
    return "you use curl 7.82.0"


# This uses a regex-string as user-agent
@app.ua_route("/", user_agent=r"curl\/[0-9.]+")
def curl_endpoint():
    return "you use curl"


if __name__ == "__main__":
    app.run(debug=True)
~~~

### fallback

this Decorater can be used to donate, that the underlying function
should be used in case the useragent does not match the user-agent-string of
the other functions.
~~~python
from flask_useragent import Flask
from flask import request

app = Flask(__name__)


@app.ua_route("/", user_agent=r"curl\/[0-9.]+")
def curl_endpoint():
    return "you use curl"


@app.fallback("/")
def fallback_endpoint():
    user_agent = request.headers.get("User-Agent")
    return f"{user_agent}"


if __name__ == "__main__":
    app.run(debug=True)
~~~


TODOs and Problems
-----

Currently, flask-useragent does not support:  
* [Variable rules](https://flask.palletsprojects.com/en/2.1.x/quickstart/#variable-rules)  
* [HTTP Methodes](https://flask.palletsprojects.com/en/2.1.x/quickstart/#http-methods)  