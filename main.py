import shutil
import os
import zipfile
import pandas as pd
import pytesseract
from PIL import Image
from django.db.models.expressions import result

# 配置路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
"""
image_folder = r'C:\test'  # 原始图片文件夹路径
excel_path = r'C:\test\数据科学与大数据技术2403班.xlsx'  # 存储学号的Excel文件路径
output_folder = r'C:\test\output'  # 保存重命名文件的文件夹路径
"""

# 解压文件
def unzip_file(zip_path):
    """
    解压指定的 zip 文件到指定目录。

    :param zip_path: zip 文件的路径
    """
    error_code = None
    path = None

    # 获取解压目标目录
    extract_dir = os.path.dirname(zip_path)

    # 确保解压目标目录存在
    os.makedirs(extract_dir, exist_ok=True)

    try:
        # 检查文件是否已存在
        if os.path.exists(zip_path):
            # 打开并解压 zip 文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            path = extract_dir
        else:
            error_code = f"错误：文件 {zip_path} 不存在。"
    except zipfile.BadZipFile:
        error_code = f"错误：{zip_path} 不是一个有效的 zip 文件。"
    except PermissionError:
        error_code = f"错误：没有权限访问 {zip_path}。"
    except Exception as e:
        error_code = f"未知错误：{e}"

    result = {
        'error': error_code,
        'path': path
    }
    return result


def zip_directory(dir_path):
    """
    压缩指定的目录到指定的输出路径。

    :param dir_path: 需要压缩的目录路径
    """
    error_code = None

    # 确保目录存在
    if not os.path.exists(dir_path):
        error_code = f"错误：目录 {dir_path} 不存在。"
    else:
        try:
            # 压缩目录
            shutil.make_archive(dir_path, 'zip', dir_path)
        except PermissionError:
            error_code = f"错误：没有权限访问 {dir_path}。"
        except Exception as e:
            error_code = f"未知错误：{e}"
    return error_code


# 文件元素检查
def check_file(folder_path):
     """
     对解压后文件的格式进行检查
     :param folder_path: 需要检查的文件目录
     """
     xlsx_found = False
     img_dir_found = False
     img_file_found = False
     xlsx_path = None
     img_dir = None
     for item in os.listdir(folder_path):
         item_path = os.path.join(folder_path, item)

         if os.path.isfile(item_path) and item.lower().endswith('.xlsx'):
             xlsx_found = True
             xlsx_path = item_path

         if os.path.isdir(item_path) and item.lower() == 'img':
             img_dir_found = True
             for file in os.listdir(item_path):
                 file_path = os.path.join(item_path, file)
                 if os.path.isfile(file_path) and file.lower().endswith(('.png', '.jpg', '.jpeg')):
                     img_file_found = True
                     img_dir = item_path
                     break

     result = {
         'xlsx_dir_found': xlsx_found,
         'xlsx_path': xlsx_path,
         'img_dir': img_dir,
         'img_dir_found': img_dir_found,
         'img_file_found': img_file_found
     }

     return result

# 文件处理函数
def file_process(image_folder, excel_path, output_folder):
    """
    主要文件处理过程
    :param image_folder: 原始图片文件夹路径
    :param excel_path: 存储学号的Excel文件路径
    :param output_folder: 保存重命名文件的文件夹路径
    """
    error_code = []
    return_code = []
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
                return_code.append(f"文件 {filename} 已重命名并保存为: {new_filepath}。\n")
                print(f"文件 {filename} 已重命名并保存为: {new_filepath}")
            else:
                error_code.append(f"未在图片 {filename} 中找到姓名或对应的学号。\n")
                print(f"未在图片 {filename} 中找到姓名或对应的学号。")
    result = {
        'error': error_code,
        'return': return_code
    }
    return result