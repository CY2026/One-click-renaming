from flask import Flask, request, send_from_directory, jsonify, make_response
import os
from main import check_file, file_process, unzip_file, zip_directory
from flask_socketio import SocketIO, emit
from queue import Queue
import threading

# 初始化Flask应用
app = Flask(__name__)
socketio = SocketIO(app)

# 定义上传目录和处理目录
UPLOAD_FOLDER = 'html/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 创建上传目录和处理目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 创建任务队列
task_queue = Queue()

# 创建线程锁
lock = threading.Lock()

def process_task(task):
    user_id, file_path = task
    with lock:
        unzipcode = unzip_file(file_path)
        if unzipcode["error"] is None:
            callback('progress', {'user_id': user_id, 'message': '文件解压完成'})
            checkfilecode = check_file(unzipcode["path"])
            if checkfilecode["xlsx_dir_found"] is True and checkfilecode["img_dir_found"] is True and checkfilecode["img_file_found"] is True:
                callback('progress', {'user_id': user_id, 'message': '文件格式正确，开始处理'})
                fileprocesscode = file_process(checkfilecode["img_dir"], checkfilecode["xlsx_path"], unzipcode["path"])
                if fileprocesscode is True:
                    callback('progress', {'user_id': user_id, 'message': '文件处理完成，等待压缩'})
                    zipcode = zip_directory(unzipcode["path"])
                    if zipcode is None:
                        callback('progress', {'user_id': user_id, 'message': '文件压缩完成，等待下发下载链接'})
                        callback('url', {'user_id': user_id, 'url': f"/download/{user_id}"})
                    else:
                        callback('error', {'user_id': user_id, 'message': '文件压缩错误，请联系网站管理员'})
                else:
                    callback('error', {'user_id': user_id, 'message': f"文件处理错误：{fileprocesscode['error']}"})
            else:
                if not checkfilecode["xlsx_dir_found"]:
                    callback('error', {'user_id': user_id, 'message': '文件格式错误：未找到xlsx文件'})
                if not checkfilecode["img_dir_found"]:
                    callback('error', {'user_id': user_id, 'message': '文件格式错误：未找到img文件夹'})
                if not checkfilecode["img_file_found"]:
                    callback('error', {'user_id': user_id, 'message': '文件格式错误：未找到img文件夹下的图片文件'})
        else:
            callback('error', {'user_id': user_id, 'error': f"文件解压错误：{unzipcode['error']}"})

def worker():
    while True:
        task = task_queue.get()
        if task is None:
            break
        process_task(task)
        task_queue.task_done()

        # 发送当前队列长度
        queue_length = task_queue.qsize()
        callback('queue_status', {'user_id': task[0], 'message': f'任务处理完成，当前队列长度：{queue_length}', 'queue_length': queue_length})


# 启动工作线程
threading.Thread(target=worker, daemon=True).start()

def callback(event, args):
    socketio.emit(event, args, namespace='/')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    上传文件并进行处理。
    用户ID和文件是通过表单数据传递的。
    文件将被保存，然后等待处理完成并提供下载链接。
    """
    user_id = request.form.get('user_id')  # 从表单数据中获取用户ID
    if not user_id:
        return jsonify({'success': False, 'message': '缺少用户ID'}), 400

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '未选择文件'}), 400
    if os.path.splitext(file.filename)[1].lower() != '.zip':
        return jsonify({'success': False, 'message': '文件格式错误：只允许zip文件'}), 400

    # 根据用户ID和文件扩展名创建子目录
    user_folder = os.path.join(UPLOAD_FOLDER, user_id)
    os.makedirs(user_folder, exist_ok=True)

    # 保存文件到子目录
    file_path = os.path.normpath(os.path.join(user_folder, file.filename))
    file.save(file_path)

    # 将任务添加到队列
    task_queue.put((user_id, file_path))

    # 发送排队状态信息
    queue_position = task_queue.qsize()
    callback('queue_status', {'user_id': user_id, 'message': f'您的任务已加入队列，当前排队位置：{queue_position}'})

    response = make_response()
    response.set_cookie('user_id', user_id)
    return response



@app.route('/download/<user_id>')
def download_file(user_id):
    """
    提供处理后的文件下载。
    用户ID和文件名是URL的一部分。
    """
    return send_from_directory('html/uploads/', f"{user_id}.zip")

@app.route('/')
def serve_root():
    """
    服务根目录的HTML文件。
    这是前端应用的入口点。
    """
    return send_from_directory('html/', 'index.html')

if __name__ == '__main__':
    socketio.run(app, port=8000, allow_unsafe_werkzeug=True)

