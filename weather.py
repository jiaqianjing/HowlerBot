import json
from os import read
from typing import Optional
import aiohttp
import asyncio
import constant

url = "http://gwgp-eo6wy9xwz4k.n.bdcloudapi.com/"
params = {
    "area": "",  # 组合1,地址查询天气,地址
    "code": "",  # 组合2,行政区划代码查天气,行政区划代码
    "ip": "",  # 组合3,IP查天气,IP地址
    "lng": "",  # 组合4,经度
    "lat": "",  # 组合4,纬度
    "region": "",  # 组合5,地域查天气,省、自治区、直辖市、特别行政区
    "city": "",  # 组合5,地域查天气,城市
    "district": ""  # 组合5,地域查天气,行政区、县
}
# Replace it with your AppCode.
headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'X-Bce-Signature': constant.X_BCE_SIGNATURE_WEATHER
}


async def get_weather(area: Optional[str]):
    params['area'] = area
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers,
                               params=params) as resp:
            result = await resp.json()
            location = result['data']['location']
            print(f"result: {location}")
            zone = location['region'] if location['region'] else ''
            zone = f"{zone} {location['city']}" if location['city'] else zone
            zone = f"{zone} {location['district']}" if location[
                'district'] else zone
            realtime = result['data']['realtime']
            w = f"""{zone}
天气: {realtime['weather']},
时间: {realtime['time']},
湿度: {realtime['airTempreture']},
风向: {realtime['windDirection']},
风力: {realtime['windForce']},
湿度: {realtime['humidity']},
空气质量: {realtime['index']['aqi']},
pm2.5: {realtime['index']['pm2.5']}
"""

            return w


if __name__ == '__main__':
    asyncio.run(get_weather('岳麓区'))
