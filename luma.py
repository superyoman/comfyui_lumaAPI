import os
import io
import json
import torch
from . import generator
from io import BytesIO
from PIL import Image

global luma_key_path
lunma_key_path = os.path.dirname(os.path.realpath(__file__))

def get_cookie_key():
    try:
        config_path = os.path.join(lunma_key_path, 'key.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        api_key = config["cookie"]
    except:
        print("Error: Cookie is required. Please enter correct cookie in key.json")
        return ""
    return api_key

def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"Fail to create the folder：{e}")

class LUMA_YoC_generator:

    def __init__(self):
        self.api_key = get_cookie_key()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"default": "movie,cinematic", "multiline": True}),
                "Enhance_prompt": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("luma_id",)
    FUNCTION = "LUMA_generation"
    CATEGORY = "YoC app/LumaAPP"

    def LUMA_generation(self,image, prompt,Enhance_prompt):
        tensor = image
        if tensor.dim() == 4 and tensor.shape[0] == 1:
            tensor = tensor.squeeze(0)  # 去掉批次维度，形状变为[3, H, W]

        # 如果通道在前，需要调整为[H, W, 3]以适应PIL或其他图像库
        if tensor.shape[0] == 3:
            tensor = tensor.permute(1, 2, 0)
        # 确保tensor是浮点类型并且范围在[0, 1]，如果不是，您可能需要先进行归一化或缩放
        tensor = tensor.clamp(0, 1)  # 确保值在[0, 1]之间

        # 判断图像是否为空白
        if torch.std(tensor) < 0.01:  # 可调整阈值以适应具体情况
            print("Empty Image")
            image_binary = None
        else:       
            # 转换为NumPy数组
            numpy_array = tensor.numpy()
            buffer = BytesIO()
            # 转换为PIL图像并保存
            image = Image.fromarray((numpy_array * 255).astype('uint8'))  # 转换为0-255范围
            image.save(buffer, format='PNG')  # 您可以选择其他格式，如JPEG
    
            # 获取二进制数据
            image_binary = buffer.getvalue()

        res = generator.DreamMachine_generation(prompt=prompt, binary_image = image_binary,
                                                Cookie=self.api_key, expand_prompt=Enhance_prompt)
        res_id = res[0]['id']
        print("Result id: %s"%res_id)
        create_folder(os.path.join(os.getcwd(), "ComfyUI/output/luma video"))
        with open(os.path.join(os.path.join(os.getcwd(), "ComfyUI/output/luma video"),"record_id.txt"), 'a') as file:
            file.write(res_id + '\n')
            
        return (res_id,)

class LUMA_YoC_result:

    def __init__(self):
        self.api_key = get_cookie_key()


    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "Enter your id", "multiline": False}),
                "download":("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_link",)
    FUNCTION = "LUMA_result"
    CATEGORY = "YoC app/LumaAPP"

    def LUMA_result(self,text,download):
        video_folder = os.path.join(os.getcwd(), "ComfyUI/output/luma video")
        create_folder(video_folder)
        res_link = generator.get_signal_video(ids = text, Cookie = self.api_key,
                        download = download,output_name=os.path.join(video_folder,f"{text}.mp4"))
        return (res_link,)

NODE_CLASS_MAPPINGS = {
    "LUMA_API_YoC": LUMA_YoC_generator,
    "LUMA_API_result_YoC": LUMA_YoC_result,

}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LUMA_API_YoC": "LUMA_generator @.@",
    "LUMA_API_result_YoC": "LUMA_YoC_result @.@",
}
