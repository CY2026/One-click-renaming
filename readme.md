### hi, all

~~~python
每位同学截图以学号姓名命名，班级以班级名称命名。各班XX委员负责。最后由2XXX班负责汇总打包发邮箱。邮箱:xxxxxxxx@example.com
~~~

相信各位班委看到这则通知，是不是有一种心脏骤停的感觉，哈哈(内心OS：我的半个小时啊！！！)

所以我就OCR技术加python写了一个简单的项目，可以用它一键实现这个任务。但我作为初学者，对于这方面不大熟悉，所以决定将其开源，希望各位大佬能帮助我一起完善这个项目！！！

### 开始之前

1. 请确保电脑上安装了 Tesseract-OCR且在安装是选择了中文支持

2. python >= 3.10 且配置环境变量
3. 已安装requirements.txt中的运行库
4. 请确保包含学号姓名的表格在所在路径中



### Usage

修改main.py中的pytesseract.pytesseract.tesseract_cmd变量为Tesseract-OCR目录

```python
example:pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

并完成配置路径中的原始图像路径，表格路径，输出路径。

然后只需要

```python
python main.py
```

等待程序运行完成即可



### 愿景

考虑到直接跑源码对于大多数人来说并不是简单的事情，所以我期望能有位会web应用开发的大佬和我一起将其改造成一个网页项目，使其更加便于使用,hihi