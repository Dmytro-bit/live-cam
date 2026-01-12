import time

from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from app.routers.device import device_auth_required

video_route = Blueprint("video", __name__)

LATEST = {
    "jpg": None,
    "ts": 0.0,
}


def mjpeg_generator():
    boundary = b"frame"
    last_sent_ts = 0.0

    while True:
        if LATEST["jpg"] is None:
            time.sleep(0.05)
            continue

        if LATEST["ts"] == last_sent_ts:
            time.sleep(0.01)
            continue

        jpg = LATEST["jpg"]
        last_sent_ts = LATEST["ts"]

        yield (
                b"--" + boundary + b"\r\n"
                                   b"Content-Type: image/jpeg\r\n"
                                   b"Content-Length: " + str(len(jpg)).encode() + b"\r\n\r\n" + jpg + b"\r\n"
        )


@video_route.route("get-next-frame")
@jwt_required()
def get_next_frame():
    return Response(
        mjpeg_generator(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@video_route.route("upload_frame")
@device_auth_required
def upload_frame():
    if "frame" not in request.files:
        return {"error": "missing form-data file field 'frame'"}, 400

    jpg = request.files["frame"].read()
    if not jpg:
        return {"error": "empty frame"}, 400

    LATEST["jpg"] = jpg
    LATEST["ts"] = time.time()
    return {"ok": True}
