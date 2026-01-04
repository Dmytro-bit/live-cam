from datetime import datetime
from flask import Flask

app = Flask(__name__)


@app.route("/health")
def health():
    return {"version": "0.0.1", "date_time": datetime.now()}


if __name__ == "__main__":
    app.run()
