from flask import Flask, request, send_from_directory, jsonify, make_response
import os
from datetime import datetime

# 初始化Flask应用
app = Flask(__name__)

# 定义上传目录和处理目录
UPLOAD_FOLDER = 'html/uploads/'
PROCESSED_FOLDER = 'html/processed/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# 创建上传目录和处理目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

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
    file_path = os.path.join(user_folder, file.filename)
    file.save(file_path)

    # 处理文件





    # 假设处理完成后生成的文件路径
    processed_file_name = f"{user_id}_{file.filename}"
    processed_file_path = os.path.join(PROCESSED_FOLDER, user_id, processed_file_name)

    # 返回下载链接
    download_url = f"/download/{user_id}/{processed_file_name}"

    # 设置用户ID到Cookies
    response = make_response(jsonify({'success': True, 'message': 'File uploaded and processing started', 'download_url': download_url}))
    response.set_cookie('user_id', user_id)

    return response

@app.route('/download/<user_id>/<filename>')
def download_file(user_id, filename):
    """
    提供处理后的文件下载。
    用户ID和文件名是URL的一部分。
    """
    return send_from_directory(os.path.join(app.config['PROCESSED_FOLDER'], user_id), filename)

@app.route('/')
def serve_root():
    """
    服务根目录的HTML文件。
    这是前端应用的入口点。
    """
    return send_from_directory('html/', 'index.html')

if __name__ == '__main__':
    app.run(port=8000)
