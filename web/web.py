from flask import Flask, request, send_from_directory
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'html/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 创建上传目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    user_id = request.form.get('user_id')  # 从表单数据中获取用户ID
    if not user_id:
        return '缺少用户ID', 400

    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return '未选择文件', 400
    if os.path.splitext(file.filename)[1].lower() != '.zip':
        return '文件格式错误：只允许zip文件', 400
    if file:
        # 根据用户ID和文件扩展名创建子目录
        user_folder = os.path.join(UPLOAD_FOLDER, user_id)
        os.makedirs(user_folder, exist_ok=True)

        # 保存文件到子目录
        file.save(os.path.join(user_folder, file.filename))
        return 'File uploaded successfully', 200

@app.route('/')
def serve_root():
    return send_from_directory('html/', 'index.html')

if __name__ == '__main__':
    app.run(port=8000)
