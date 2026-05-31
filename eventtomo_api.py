from flask import Flask, request, jsonify, send_file
import json, os, subprocess

app = Flask(__name__)
DAYS_FILE = '/root/eventtomo-bot/days.json'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_REPO = 'husseinalsafi/eventtomo-bot'

@app.route('/eventtomo/api/days', methods=['GET'])
def get_days():
    with open(DAYS_FILE, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))

@app.route('/eventtomo/api/save', methods=['POST'])
def save_days():
    data = request.json
    with open(DAYS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({'ok': True, 'type': 'local'})

@app.route('/eventtomo/api/backup', methods=['POST'])
def backup_to_github():
    data = request.json
    with open(DAYS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    try:
        os.chdir('/root/eventtomo-bot')
        subprocess.run(['git', 'add', 'days.json'], check=True)
        subprocess.run(['git', 'commit', '-m', 'backup: update days.json from admin panel'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        return jsonify({'ok': True, 'type': 'github'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
