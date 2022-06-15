# coding: utf-8
from PIL import Image
import shutil
import os
import json
from datetime import datetime


class Graphics:
    def __init__(self, infile, outfile):
        self.infile = infile
        self.outfile = outfile

    def fixed_size(self, width, height):
        """按照固定尺寸处理图片"""
        im = Image.open(self.infile)
        out = im.resize((width, height), Image.ANTIALIAS)
        out.save(self.outfile)

    def resize_by_width(self, w_divide_h):
        """按照宽度进行所需比例缩放"""
        im = Image.open(self.infile)
        (x, y) = im.size
        x_s = x
        y_s = x / w_divide_h
        out = im.resize((x_s, y_s), Image.ANTIALIAS)
        out.save(self.outfile)

    def resize_by_height(self, w_divide_h):
        """按照高度进行所需比例缩放"""
        im = Image.open(self.infile)
        (x, y) = im.size
        x_s = y * w_divide_h
        y_s = y
        out = im.resize((x_s, y_s), Image.ANTIALIAS)
        out.save(self.outfile)

    def resize_by_size(self, size):
        """按照生成图片文件大小进行处理(单位KB)"""
        size *= 1024
        im = Image.open(self.infile)
        size_tmp = os.path.getsize(self.infile)
        q = 100
        while size_tmp > size and q > 0:
            print(q)
            out = im.resize(im.size, Image.ANTIALIAS)
            out.save(self.outfile, quality=q)
            size_tmp = os.path.getsize(self.outfile)
            q -= 5
        if q == 100:
            shutil.copy(self.infile, self.outfile)

    def cut_compress(self):
        im = Image.open(self.infile)
        (x, y) = im.size
        if x > y:
            region = (int(x / 2 - y / 2), 0, int(x / 2 + y / 2), y)
        else:
            region = (0, int(y / 2 - x / 2), x, int(y / 2 + x / 2))
        # 裁切图片
        crop_img = im.crop(region)
        w, h = crop_img.size
        crop_img.thumbnail((int(w / SIZE_more_small_small), int(h / SIZE_more_small_small)))
        path = self.outfile[:self.outfile.rindex('/')]
        if not os.path.exists(path):
            os.makedirs(path)
        crop_img.save(self.outfile)


SRC_DIR = "photos"
DES_DIR = "min_photos"
SIZE_normal = 1.0
SIZE_small = 1.5
SIZE_more_small = 2.0
SIZE_more_small_small = 3.0


def list_img_file(directory):
    res = []
    for root, ds, fs in os.walk(directory):
        for f in fs:
            _, form = f.split(".")
            if form.lower() == "jpg" or form.lower() == "png" or form.lower() == "gif":
                res.append(os.path.join(root, f))
    return res


def handle_photo():
    github_img_path = "https://raw.githubusercontent.com/cherish-merry/album/master/"
    src_file_list = list_img_file(SRC_DIR)
    des_file_list = list_img_file(DES_DIR)
    git_dict = {"photos": [], "min_photos": []}
    for i in range(len(src_file_list)):
        git_dict['photos'].append(github_img_path + src_file_list[i])
    for i in range(len(des_file_list)):
        git_dict['min_photos'].append(github_img_path + des_file_list[i])
    with open("/Volumes/MAC-WIN/album/data.json", "w") as fp:
        json.dump(git_dict, fp)


def cut_compress():
    src_file_list = list_img_file(SRC_DIR)
    des_file_list = list_img_file(DES_DIR)
    des_file_name = []
    for i in range(len(des_file_list)):
        path = des_file_list[i]
        des_file_name.append(path[path.index('/'):])

    for i in range(len(src_file_list)):
        path = src_file_list[i]
        if path[path.index('/'):] not in des_file_name:
            Graphics(infile=path, outfile=DES_DIR + path[path.index('/'):]).cut_compress()


def git_operation():
    os.system('git add --all')
    os.system('git commit -m "add photos"')
    os.system('git push origin master')


cut_compress()  # 裁剪图片，裁剪成正方形，去中间部分
git_operation()  # 提交到github仓库
handle_photo()  # 将文件处理成json格式，存到博客仓库中
