# use deep learning model te detect the handwriting characters here
import os
from ocr import ocr
import time
import numpy as np
from PIL import Image


def single_pic_proc(img_path):
    image = np.array(Image.open(img_path).convert('RGB'))
    result, image_framed = ocr(image)
    return result, image_framed


def process_img(img_path):
    result_dir = './outputs'
    os.makedirs(result_dir, exist_ok=True)

    result, image_framed = single_pic_proc(img_path)
    output_file = os.path.join(result_dir, img_path.split('\\')[-1])
    txt_file = os.path.join(result_dir, img_path.split('\\')[-1].split('.')[0] + '.txt')
    print(output_file, txt_file)
    Image.fromarray(image_framed).save(output_file)

    with open(txt_file, 'w+') as f:
        for key in result:
            if result[key][1]:
                f.write(result[key][1] + '\n')
        f.seek(0)
        txt = f.read()[:-1]
    print(txt)
    return txt