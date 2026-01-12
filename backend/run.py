from datetime import datetime
from flask import render_template
from app import create_app

app = create_app()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return {"version": "0.0.1", "date_time": datetime.now()}


if __name__ == "__main__":
    app.run()
