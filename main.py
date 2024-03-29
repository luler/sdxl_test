import io
import json
import os

import dotenv
import gradio as gr
import requests
import retrying
from PIL import Image


@retrying.retry(stop_max_attempt_number=5, wait_fixed=1000)
def translate(text):
    with requests.get('https://lingva.thedaviddelta.com/api/v1/auto/en/' + text) as response:
        text = ''
        if response.status_code == 200:
            data = response.json()
            text = data['translation']
        return text


@retrying.retry(stop_max_attempt_number=10, wait_fixed=1000)
def get_image_url(text):
    headers = {
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + os.getenv('MYSTICAI_API_KEY'),
    }
    data = {
        "pipeline": "ainzoil/sd-xl:v15",
        "inputs": [
            {
                "type": "string",
                "value": text
            },
            {
                "type": "dictionary",
                "value": {
                    "batch": 1,
                    "denoising_end": 0.8,
                    "guidance_scale": 7,
                    "height": 1024,
                    "negative_prompt": " ",
                    "num_inference_steps": 50,
                    "seed": 0,
                    "width": 1024
                }
            }
        ]
    }
    with requests.post('https://www.mystic.ai/v4/runs', data=json.dumps(data), headers=headers) as response:
        res = response.json()
        return res['outputs'][0]['value'][0]['file']['url']


def sdxl(text):
    image_url = get_image_url(text)
    with requests.get(image_url) as response_image:
        img = Image.open(io.BytesIO(response_image.content))
        return img


def dosomething(text):
    return sdxl(translate(text))


# 这里是主程序的代码
if __name__ == "__main__":
    # 加载配置
    dotenv.load_dotenv()

    ii = gr.Textbox(label='图片描述')
    oo = gr.Image(label='生成的图片')

    demo = gr.Interface(dosomething, inputs=ii, outputs=oo, title='基于Stable Diffusion模型的图片生成')

    demo.launch(server_name='0.0.0.0', server_port=7860)
