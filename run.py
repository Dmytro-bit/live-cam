from datetime import datetime
from app import create_app

app = create_app()


@app.route("/health")
def health():
    return {"version": "0.0.1", "date_time": datetime.now()}


if __name__ == "__main__":
    app.run()
