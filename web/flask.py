from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)


@app.route('/')
def index():
    return render_template_string('''
        <form action="/upload" method="post" enctype="multipart/form-data">
            选择文件: <input type="file" name="file"><br>
            <input type="submit" value="上传">
        </form>
    ''')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "没有文件部分"
    file = request.files['file']
    if file.filename == '':
        return "没有选择文件"
    if file:
        # 处理文件
        result = process_file(file)
        # 返回处理后的文件
        return send_file(result, as_attachment=True)


def process_file(file):
    # 这里可以添加文件处理逻辑
    # 例如保存文件、修改文件内容等
    filename = file.filename
    file.save(filename)  # 保存文件到当前目录
    # 假设处理后文件名为 processed_filename
    processed_filename = f"processed_{filename}"
    # 模拟处理过程
    with open(processed_filename, 'w') as f:
        f.write("这是处理后的文件内容")
    return processed_filename


if __name__ == '__main__':
    app.run(debug=True)
