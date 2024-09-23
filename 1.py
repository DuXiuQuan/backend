from flask import Flask, jsonify, request
import secrets
import requests

app = Flask(__name__)

device_bindings = {}
device_status = {}
devices = {
    '1': {'name': 'alice', 'id': '1'},
}

@app.route('/bind_device', methods=['POST'])
def bind_device():
    token = secrets.token_hex(16)
    user_ip = request.remote_addr
    device_bindings[token] = user_ip
    return jsonify({"status": "success", "token": token}), 200

@app.route('/verify_device', methods=['POST'])
def verify_device():
    data = request.json
    token = data.get('token')

    if token not in device_bindings:
        return jsonify({"status": "error", "message": "Invalid or expired token"}), 403

    user_ip = request.remote_addr
    bound_ip = device_bindings[token]

    if user_ip == bound_ip:
        return jsonify({"status": "success", "message": "Device bound successfully!"}), 200

@app.route('/login', methods=['POST'])
def login_device():
    username = request.form['username']
    ip_address = request.form['ip']

    login_data = {
        'username': username,
        'ip': ip_address,
    }
    try:
        response = requests.post('https://yxms.byr.ink/api/login', data=login_data)
        response.raise_for_status()

        device_status[ip_address] = True
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Login request failed', 'details': str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout_device():
    device_id = request.form['device_id']
    device_status[device_id] = False
    return jsonify({'message': 'Logout successful', 'device': device['name']}), 200

@app.route('/devices/<token>', methods=['DELETE'])
def unbind_device(token):
    if token in device_bindings:
        del device_bindings[token]
        return jsonify({"status": "success", "message": "Device unbound successfully!"}), 200
    return jsonify({"message": "Token not found"}), 404

@app.route('/devices', methods=['GET'])
def list_devices():
    devices_list = []
    for device_id, device_info in devices.items():
        devices_list.append({
            "id": device_info['id'],
            "ip": request.remote_addr,
            "logged_in": device_status.get(device_info['id'], False)
        })
    return jsonify({"status": "success", "devices": devices_list}), 200

if __name__ == '__main__':
    app.run(debug=True)
