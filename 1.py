from flask import Flask, jsonify, request
import secrets
import requests

app = Flask(__name__)

devices = []
id_counter = 0


@app.route('/bind', methods=['POST'])
def bind_device():
    global id_counter
    token = secrets.token_hex(16)
    user_ip = request.remote_addr
    devices.append({
        'token': token,
        'ip': user_ip,
        'logged_in': False,
        'username': None,
        'id': id_counter
    })
    id_counter += 1
    return jsonify({"status": "success", "token": token}), 200


@app.route('/verify', methods=['POST'])
def verify_device():
    data = request.json
    token = data.get('token')
    user_ip = request.remote_addr

    for device in devices:
        if device['token'] == token and device['ip'] == user_ip:
            return jsonify({"status": "success", "message": "Device bound successfully!"}), 200

    return jsonify({"status": "error", "message": "Invalid token or IP"}), 403


@app.route('/devices/<int:id>/login', methods=['POST'])
def login_device(id):
    data = request.json
    username = data.get('username')

    for device in devices:
        if device['id'] == id:
            login_data = {
                'username': username,
                'ip': device['ip'],
            }
            try:
                response = requests.post('http://localhost:3000/api/login', json=login_data)
                response.raise_for_status()
                device['logged_in'] = True
                return jsonify({"status": "success", "message": "Device logged in successfully!"})

            except requests.exceptions.RequestException as e:
                return jsonify({'error': 'Login request failed', 'details': str(e)}), 500

    return jsonify({'status': 'error', 'message': 'Device not found'}), 404


@app.route('/devices/<int:id>/logout', methods=['POST'])
def logout_device(id):
    for device in devices:
        if device['id'] == id:
            device['logged_in'] = False
            return jsonify({'status': 'success', 'message': 'Device logged out successfully'}), 200

    return jsonify({'status': 'error', 'message': 'Device not found or already logged out'}), 404


@app.route('/devices', methods=['GET'])
def list_devices():
    devices_list = [
        {
            'id': device['id'],
            'ip': device['ip'],
            'logged_in': device['logged_in'],
        }
        for device in devices
    ]
    return jsonify({"status": "success", "devices": devices_list}), 200



@app.route('/devices/<int:id>', methods=['DELETE'])
def unbind_device(id):
    global devices
    devices = [device for device in devices if device['id'] != id]
    return jsonify({"status": "success", "message": "Device unbound successfully!"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
