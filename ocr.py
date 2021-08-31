"""
baidu cloud api:
    https://cloud.baidu.com/apiexplorer/index.html?Product=GWSE-DJAQ8YwekkQ&Api=GWAI-gsbcdCuBWRC
"""
import asyncio
import base64
import json
import urllib.parse
from os import O_RSYNC, read
from typing import Mapping, Optional

import aiohttp

import constant

token_url = "https://aip.baidubce.com/oauth/2.0/token"
ocr_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"

headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

# Replace it with your API Key and Secret Key.
token_params = {
    "grant_type": "client_credentials",
    "client_id": constant.API_KEY,  # API Key
    "client_secret": constant.SECRET_KEY  #Secret Key
}

ocr_params = {
    "access_token": None,
}

# api reference: https://cloud.baidu.com/doc/OCR/s/7kibizyfm
ocr_body: Mapping = {
    "image": None,  # 图像base64编码
    "language_type":
    "auto_detect",  # 图像数据，base64编码，要求base64编码后大小不超过4M，最短边至少15px，最长边最大4096px,支持jpg/png/bmp格式
    "recognize_granularity":
    "small",  # 是否定位单字符位置，big：不定位单字符位置，默认值；small：定位单字符位置
    "detect_direction": "true",  # 是否检测图像朝向，默认不检测
    "vertexes_location": "true",  # 是否返回文字外接多边形顶点位置，不支持单字位置。
    "paragraph": "true",  # 检测段落
    "probability": "true",
}


async def get_content_from_img(img_path: Optional[str]):
    async with aiohttp.ClientSession() as session:
        with open(img_path, "rb") as f:
            image = base64.b64encode(f.read())
        async with session.get(url=token_url,
                               headers=headers,
                               params=token_params) as resp:
            response = await resp.json()
            access_token = response.get("access_token")
            ocr_params['access_token'] = access_token
            ocr_body['image'] = image
            print(f'ocr_params: {ocr_params}')
            data = urllib.parse.urlencode(ocr_body)
        async with session.post(url=ocr_url,
                                headers=headers,
                                params=ocr_params,
                                data=data) as resp:
            response = await resp.json()
            words = [r['words'] for r in response['words_result']]
            words = '/n'.join(words)
            print(words)
            return words


if __name__ == '__main__':
    asyncio.run(get_content_from_img('./img/demo-01.png'))
