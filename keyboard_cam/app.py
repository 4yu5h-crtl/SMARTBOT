from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# ESP32 Bot Configuration
ROBOT_URL = 'http://192.168.29.100/control'  # Change to match your ESP32 bot's URL
CAMERA_URL = 'http://192.168.29.134:8080/video'  # Change to match your ip from the app

@app.route('/')
def index():
    """Render the web interface."""
    return render_template('index.html', camera_url=CAMERA_URL)

@app.route('/control', methods=['POST'])
def control():
    """Handle movement commands via HTTP."""
    command = request.form.get('command')
    velocity = request.form.get('velocity', 100)  # Default velocity = 100

    try:
        url = f"{ROBOT_URL}?command={command}&speed={velocity}"
        response = requests.get(url, timeout=1)
        return "OK" if response.status_code == 200 else "Failed", response.status_code
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Accessible from LAN
