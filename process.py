# use deep learning model te detect the handwriting characters here
from icecream import ic
import os
from ocr import ocr
import time
import numpy as np
from PIL import Image
import zipfile
import base64


def single_pic_proc(img_path, handwriting=True):
    image = np.array(Image.open(img_path).convert('RGB'))
    result, image_framed = ocr(image, handwriting)
    return result, image_framed


def process_img(img_path, handwriting=True):
    lines = []
    result, image_framed = single_pic_proc(img_path, handwriting)
    for key in result:
        if result[key][1]:
            lines.append(result[key][1])
    txt = '\n'.join(lines)
    return txt


def zip_test(test_name):
    test_path = f'./uploads/{test_name}'

    with zipfile.ZipFile(f'{test_name}.zip', 'w', zipfile.ZIP_DEFLATED) as f:
        for path, dirnames, filenames in os.walk(test_path):
            fpath = path.replace(test_path, '')

            for filename in filenames:
                f.write(os.path.join(path, filename), os.path.join(fpath, filename))




def return_img_stream(img_path):
    img_stream = ''
    with open(img_path, 'rb') as img:
        img_stream = img.read()
        img_stream = base64.b64encode(img_stream)
    return img_stream

def get_test_ans_img(test_name):
    ans_path = os.path.join()


if __name__ == '__main__':
    zip_test('COMP311-MinTern')