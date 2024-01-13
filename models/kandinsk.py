import json
import time
import os
from PIL import Image
import requests 
import io
import base64


# 生图 API ________________________________________________________________
class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url # https://api-key.fusionbrain.ai/
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

	# 获取模型 ID
    def get_model(self):
        # requests.post 方法会自动识别 files 参数的内容，并设置正确的 Content-Type，这是 requests 库的内置行为
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        if response.status_code == 200:
            data = response.json()
            return data[0]['id']
        else:
            print(f"API 请求失败，状态码：{response.status_code}")
            return None

	# 请求模型生成图片
    def generate(self, prompt_content, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt_content}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

	# 轮询检查图片生成状态
    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)