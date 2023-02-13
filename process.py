# use deep learning model te detect the handwriting characters here
from icecream import ic
import os
from ocr import ocr
import time
import numpy as np
from PIL import Image


def single_pic_proc(img_path):
    image = np.array(Image.open(img_path).convert('RGB'))
    result, image_framed = ocr(image)
    return result, image_framed


def process_img(ans_path):
    result_dir = os.path.join(ans_path, 'outputs')
    os.makedirs(result_dir, exist_ok=True)
    img_list = os.listdir(ans_path)
    img_list.remove('outputs')

    result_txt = os.path.join(result_dir, f'ans.txt')

    with open(result_txt, 'w+') as f:
        for img in img_list:
            img_path = os.path.join(ans_path, img)
            result, image_framed = single_pic_proc(img_path)

            name = img.split('.')[1]
            result_img = os.path.join(result_dir, f'{name}.png')

            Image.fromarray(image_framed).save(result_img)
            for key in result:
                if result[key][1]:
                    f.write(result[key][1] + '\n')
        f.seek(0)
        txt = f.read()[:-1]
    return txt
