import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def is_extension_allowed(extension):
    return extension in ALLOWED_EXTENSIONS


def clean_files(max_num):
    dir_list = os.listdir('uploads')
    if not dir_list or len(dir_list) <= max_num:
        return
    dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join('uploads', x)))
    for i in range(len(dir_list) - max_num):
        os.remove(os.path.join('uploads', dir_list[i]))


if __name__ == '__main__':
    clean_files()
