from flask import Blueprint, request, render_template, jsonify
from flask_jwt_extended import jwt_required

from app.database import db
from app.models.device import Device
from app.vendors.pubnub.client import CLIENT

control_route = Blueprint("control", __name__)


@control_route.route("/servo", methods=["GET"])
@jwt_required()
def servo_control():
    devices = db.session.execute(db.select(Device)).scalars().all()
    device_id = request.args.get("device_id", type=int)

    selected_device = None
    if device_id:
        selected_device = db.session.get(Device, device_id)

    return render_template("control/servo.html", devices=devices, selected_device=selected_device)


@control_route.route("/api/publish-servo", methods=["POST"])
@jwt_required()
def publish_servo():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    channel_name = data.get("channel_name")
    x_axis = data.get("x_axis")
    y_axis = data.get("y_axis")

    if channel_name is None or x_axis is None or y_axis is None:
        return jsonify({"error": "Missing required fields: channel_name, x_axis, y_axis"}), 400

    if not (-90 <= x_axis <= 90) or not (-90 <= y_axis <= 90):
        return jsonify({"error": "x_axis and y_axis must be between -90 and 90"}), 400

    device = db.session.execute(
        db.select(Device).filter_by(chanel_name=channel_name)
    ).scalar_one_or_none()

    if not device:
        return jsonify({"error": "Device not found"}), 404

    message = {
        "request_type": "change_servomotors_position",
        "servomotors-angle": {
            "x-axis": int(x_axis),
            "y-axis": int(y_axis)
        }
    }

    try:
        CLIENT.publish(channel_name, message)
        return jsonify({"success": True, "message": "Published successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
