from functools import wraps

from flask import Blueprint, request, jsonify

from app.database import db
from app.models.device import Device
from app.vendors.pubnub.client import CLIENT

device_route = Blueprint("device", __name__)


def device_auth_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        certificate_string = request.headers.get("certificate-string")
        device_id = request.headers.get("device-id")

        if not certificate_string or not device_id:
            return jsonify({"error": "Missing certificate-string or device-id headers"}), 400

        try:
            device_id_int = int(device_id)
        except ValueError:
            return jsonify({"error": "device-id must be integer"}), 400

        device = db.session.execute(
            db.select(Device).filter_by(
                id=device_id_int,
                certificate_string=certificate_string
            )
        ).scalar_one_or_none()

        if not device:
            return jsonify({"error": "Device not found"}), 404

        kwargs["device"] = device
        return func(*args, **kwargs)

    return decorated_function


@device_route.route("/register", methods=["POST"])
@device_auth_required
def register(device: Device):
    channel_name = device.chanel_name

    if channel_name:
        return {"error": "Device already registered"}, 400

    channel_name = CLIENT.generate_chanel_name(str(device.id))
    device.chanel_name = channel_name
    db.session.commit()

    token = CLIENT.grant_channel_access(channel_name, str(device.id))

    return {
        "channel": channel_name,
        "token": token
    }


@device_route.route("/refresh-token", methods=["POST"])
@device_auth_required
def refresh_token(device: Device):
    channel_name = device.chanel_name

    if not channel_name:
        return {"error": "Device not registered"}, 400

    token = CLIENT.grant_channel_access(channel_name, str(device.id))

    return {"token": token}
