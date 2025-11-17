from main import gemini_api_call

from flask import Flask, request

app = Flask(__name__)


@app.route("/gemini", methods=["POST", "OPTIONS"])
def gemini():
    return gemini_api_call(request)


if __name__ == "__main__":
    app.run(debug=True)
