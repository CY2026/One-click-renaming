import pytesseract
from PIL import Image
import pandas as pd
import os

# 配置路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
image_folder = r'C:\test'  # 原始图片文件夹路径
excel_path = r'C:\test\数据科学与大数据技术2403班.xlsx'  # 存储学号的Excel文件路径
output_folder = r'C:\test\output'  # 保存重命名文件的文件夹路径

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 读取 Excel 表格，提取学生姓名和学号的对应关系
student_data = pd.read_excel(excel_path)
student_data.columns = student_data.columns.str.strip()  # 清除列名中的空格

# 构建学号-姓名字典，并确保学号为字符串，去掉任何小数点或 .0
student_dict = {str(name).strip(): str(student_id).split('.')[0] for name, student_id in zip(student_data['姓名'], student_data['学号'])}

# 遍历图片文件夹中的所有图片
for filename in os.listdir(image_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(image_folder, filename)
        image = Image.open(image_path)

        # 使用OCR提取文本
        extracted_text = pytesseract.image_to_string(image, lang='chi_sim')

        # 查找姓名信息
        name = None
        for line in extracted_text.splitlines():
            for student_name in student_dict.keys():
                if isinstance(student_name, str) and student_name in line:  # 确保 student_name 是字符串
                    name = student_name
                    break
            if name:
                break

        # 检查是否找到对应学号，并重命名文件
        if name and name in student_dict:
            student_id = student_dict[name]
            new_filename = f"{student_id}{name}.png"
            new_filepath = os.path.join(output_folder, new_filename)
            image.save(new_filepath)
            print(f"文件 {filename} 已重命名并保存为: {new_filepath}")
        else:
            print(f"未在图片 {filename} 中找到姓名或对应的学号。")
