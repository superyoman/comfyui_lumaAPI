import requests
import time

global lumalabs_internal_url,COMMON_HEADERS

lumalabs_internal_url = 'https://internal-api.virginia.labs.lumalabs.ai/api/photon/v1/generations/'
COMMON_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50",
    "Referer": "https://lumalabs.ai/",
    "Origin": "https://lumalabs.ai",
}

def get_video_response(ids):
    api_url = f"{lumalabs_internal_url}/{ids}"
    response = requests.get(url = api_url,headers = COMMON_HEADERS)
    return response.json()

def get_video(ids):
    res = get_video_response(ids)
    if "id" in res:
        print(type(res))
        return res['video']

def get_upload_link(Cookie):
    full_url = f"{lumalabs_internal_url}file_upload"
    params = {
        'file_type': 'image',
        'filename': 'file.jpg'
    }
    response = requests.post(full_url, params = params, cookies = Cookie)
    presigned_url, public_url = response.json()["presigned_url"], response.json()["public_url"]
    print(presigned_url)
    print(public_url)
    return presigned_url, public_url

def upload_file(Cookie, file_path):
    try:
        presigned_url, public_url =  get_upload_link(Cookie)
        time.sleep(1)
        with open(file_path, 'rb') as file:
            response = requests.put(presigned_url, data=file,
                        headers={'Content-Type': "image/*", "Referer": "https://lumalabs.ai/", "origin": "https://lumalabs.ai"})

        if response.status_code == 200:
            print("Upload successful:", public_url)
            return public_url
        else:
            print("Upload failed.")
    except Exception as e:
        print("Upload failed:", e)


def upload_file_comfyui(Cookie, binary_image):
    try:
        presigned_url, public_url = get_upload_link(Cookie)
        time.sleep(1)
        response = requests.put(presigned_url, data=binary_image,
                        headers={'Content-Type': "image/*", "Referer": "https://lumalabs.ai/", "origin": "https://lumalabs.ai"})

        if response.status_code == 200:
            print("Upload successful:", public_url)
            return public_url
        else:
            print("Upload failed.")
    except Exception as e:
        print("Upload failed:", e)

def DreamMachine_generation(prompt,Cookie,image_file = None,binary_image = None, expand_prompt = True):
    payload = {
        "user_prompt": prompt,
        "aspect_ratio": "16:9",
        "expand_prompt": expand_prompt
    }
    Cookie_dict = {
        "Cookie":Cookie
    }
    if image_file:
        image_url = upload_file(Cookie_dict, image_file)
        if image_url.startswith("https:"):
            payload["image_url"] = image_url
        else:
            return "Something Wrong"

    if binary_image:
        image_url = upload_file_comfyui(Cookie_dict, binary_image)
        if image_url.startswith("https:"):
            payload["image_url"] = image_url
        else:
            return "Something Wrong"


    response = requests.post(lumalabs_internal_url, json=payload, cookies = Cookie_dict, headers=COMMON_HEADERS)
    response_json = response.json()
    return response_json

def check_res(Cookie = str):
    try:
        url =  "https://internal-api.virginia.labs.lumalabs.ai/api/photon/v1/user/generations/"
        params = {"offset": "0", "limit": "10"}
        res = requests.get(url,headers = {"Cookie":Cookie},params = params)
        return res.json()
    except Exception as ex:
        print("Failed to get result: %s"%ex)

def get_signal_video(ids = str,Cookie = str,download = True, output_name = 'output_video.mp4'):
    res = check_res(Cookie)
    for i in res:
        if ids == i['id']:
            video_url = i["video"]['url']
            if download:
                with open(output_name, 'wb') as file:
                    response = requests.get(video_url, stream=True)
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
            return video_url
    return "No result"

if __name__ == "__main__":
    pass