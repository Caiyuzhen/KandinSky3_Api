import os
import io
from io import BytesIO
import base64
from PIL import Image


def save_image_to_system(base64_string, save_path):
	# 将 base64 字符串【解码】成二进制数据
	image_data = base64.b64decode(base64_string)

	# 使用 BytesIO 将二进制数据转换成图片对象
	image = Image.open(BytesIO(image_data))

	# 生成唯一的文件名（使用自增序号）
	image_number = 1
	image_path = f"{save_path}image_{image_number}.png"
	print(f"✅ 图片保存路径: {image_path}")
	while os.path.exists(image_path):
		image_number += 1
		image_path = f"{save_path}image_{image_number}.png"

	# 保存图片到文件系统
	image.save(image_path)
	return image_path