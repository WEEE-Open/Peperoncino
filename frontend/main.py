from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import threading
from werkzeug.utils import secure_filename
from queue import Queue
import time
import mimetypes

app = Flask(__name__, template_folder='src')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'svg', 'gcode', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
app.config['SERVER_IP'] = ''
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

file_queue = Queue()
queue_lock = threading.Lock()
processing_thread = None
processing_paused = False

# Track individual file statuses
file_status = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_queue():
    while True:
        with queue_lock:
            if not processing_paused and not file_queue.empty():
                file_data = file_queue.queue[0]
                file_data['status'] = 'Processing'
                file_status[file_data['name']] = 'Processing'
                
                # Simulate file processing
                time.sleep(5)
                if file_data['type'] in ['svg', 'png', 'jpg', 'jpeg', 'gif']:
                    file_data['status'] = 'Converted'
                    file_status[file_data['name']] = 'Converted'
                else:
                    file_data['status'] = 'Completed'
                    file_status[file_data['name']] = 'Completed'
                file_queue.get()
            else:
                time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set-ip', methods=['POST'])
def set_ip():
    ip = request.form.get('server_ip')
    if not ip or len(ip.split('.')) != 4:
        return jsonify({'error': 'Invalid IP address'}), 400
    app.config['SERVER_IP'] = ip
    return jsonify({'status': 'success'})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_type = filename.rsplit('.', 1)[1].lower()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        file_data = {
            'name': filename,
            'type': file_type,
            'status': 'Pending',
            'path': file_path
        }
        
        with queue_lock:
            file_queue.put(file_data)
            file_status[filename] = 'Pending'
        
        return jsonify({
            'name': filename,
            'type': file_type,
            'preview': f"/uploads/{filename}" if file_type in ['png', 'jpg', 'jpeg', 'gif', 'svg'] else None
        })
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/queue/status')
def queue_status():
    with queue_lock:
        queue_list = []
        for item in list(file_queue.queue):
            queue_list.append({
                'name': item['name'],
                'type': item['type'],
                'status': item['status']
            })
    return jsonify({
        'queue': queue_list,
        'paused': processing_paused
    })

@app.route('/file/control/<action>/<filename>', methods=['POST'])
def file_control(action, filename):
    with queue_lock:
        if action == 'start':
            if filename in file_status:
                file_status[filename] = 'Processing'
        elif action == 'pause':
            if filename in file_status:
                file_status[filename] = 'Paused'
        elif action == 'remove':
            if filename in file_status:
                del file_status[filename]
                # Remove from queue (simplified for example)
                new_queue = Queue()
                while not file_queue.empty():
                    item = file_queue.get()
                    if item['name'] != filename:
                        new_queue.put(item)
                file_queue.queue = new_queue.queue
        return jsonify({'status': 'success'})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
           
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    processing_thread = threading.Thread(target=process_queue, daemon=True)
    processing_thread.start()
    app.run(debug=True)