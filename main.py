import os
import random
from flask import Flask, request, jsonify
from threading import Thread
from datetime import datetime
from utils.save_image import save_image_to_system
from models.kandinsk import Text2ImageAPI
from flask import Flask, request, jsonify, send_from_directory # 使用Flask的send_from_directory函数来提供静态文
import socket # 用于获取当前服务器的 ip


app = Flask(__name__)

# 生图的存放路径 => os.getcwd() 获取当前工作目录
OUTPUT_FOLDER = os.path.join(os.getcwd(), 'outputs/')
API_URL = "https://api-key.fusionbrain.ai/"
# SERVER_IP = "127.0.0.1" # 服务器地址, 用于生成图片的 URL
# SERVER_IP = os.environ.get('SERVER_IP')
PORT = 9090 # 服务器端口, 跟服务器启动的端口号一样, 用于生成图片的 URL
# 从环境变量中获取 SERVER_IP

# 获取服务器的IP地址
def get_server_ip():
    try:
        # 这里使用一个连接到互联网的地址来获取主机名
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception as e:
        print(f"Error getting server IP: {e}")
        return None
    finally:
        s.close()

# 服务器IP地址
SERVER_IP = get_server_ip()


# 生图服务的路由 👉  http://127.0.0.1:8000/generateImage
# 格式为:
# {
#	"api_key": "xxx",
#	"secret_key": "xxx",
#	"prompt_content": "xxx"
# }
 
@app.route('/generateImage', methods=['POST'])
def index():
    # 鉴权
    API_KEY = request.json.get('api_key') # 从 POST 数据中获取 api_key 参数
    SECRET_KEY = request.json.get('secret_key') # 从 POST 数据中获取 secret_key 参数
    PROMPT_CONTENT = request.json.get('prompt_content') # 从 POST 数据中获取 prompt_content 参数
    print(f"✅ 拿到了参数: ", API_KEY, SECRET_KEY, PROMPT_CONTENT)
    
    # 进行生图
    api_Instance = Text2ImageAPI(API_URL, API_KEY, SECRET_KEY)
    
    # 传入 Prompt, 获取生图模型 ID
    model_id = api_Instance.get_model()
    uuid = api_Instance.generate(PROMPT_CONTENT, model_id)
    print(f"✅ 拿到了 model_id: ", model_id)
    # uuid = api_Instance.generate("A cute robot cat", model_id)
    
    # 查询生图状态, 并返回图片的 base64 字符串
    base64_string = api_Instance.check_generation(uuid) ## 从 API 获取的 base64 字符串
    # print(f"✅ 拿到了 base64_string: ", base64_string)
    
    # 保存图片到文件系统, 使用 os 会更灵活的适配不同的操作系统
    if not os.path.exists(OUTPUT_FOLDER): # 没有则创建文件夹
        os.mkdir(OUTPUT_FOLDER) 
        
    image_path = save_image_to_system(base64_string[0], OUTPUT_FOLDER) # 保存图片
    image_url = f"http://{SERVER_IP}:{PORT}/images/{os.path.basename(image_path)}" # 将保存路径转换为图片的 URL
    # image_url = f"http://{SERVER_IP}:9090/images/{os.path.basename(image_path)}" # 将保存路径转换为图片的 URL
    print(f"✅ 图片 URL: {image_url}")
    
    return jsonify({
		'image_path': image_url
	})
    
    
@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(OUTPUT_FOLDER, filename) # 通过 http://127.0.0.1:8000/images/image_xxx.png 来访问图片



# 初始化 __main__, 开启服务
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=PORT, debug=True)
#  app.run(host="0.0.0.0", port={9090}, debug=True)
