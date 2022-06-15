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
        crop_img.save(self.outfile)


SRC_DIR = "./photos/"
DES_DIR = "./min_photos/"
SIZE_normal = 1.0
SIZE_small = 1.5
SIZE_more_small = 2.0
SIZE_more_small_small = 3.0


def list_img_file(directory):
    """列出目录下所有文件，并筛选出图片文件列表返回"""
    old_list = os.listdir(directory)
    new_list = []
    for filename in old_list:
        name, formant = filename.split(".")
        if formant.lower() == "jpg" or formant.lower() == "png" or formant.lower() == "gif":
            new_list.append(filename)
    return new_list


def handle_photo():
    file_list = list_img_file(SRC_DIR)
    list_info = []
    for i in range(len(file_list)):
        filename = file_list[i]
        date_str, *info = filename.split("_")
        info = '_'.join(info)
        info, _ = info.split(".")
        date = datetime.strptime(date_str, "%Y-%m-%d")
        year_month = date_str[0:7]
        if i == 0:  # 处理第一个文件
            new_dict = {"date": year_month, "arr": {'year': date.year,
                                                    'month': date.month,
                                                    'link': [filename],
                                                    'text': [info],
                                                    'type': ['image']
                                                    }
                        }
            list_info.append(new_dict)
        elif year_month != list_info[-1]['date']:  # 不是最后的一个日期，就新建一个dict
            new_dict = {"date": year_month, "arr": {'year': date.year,
                                                    'month': date.month,
                                                    'link': [filename],
                                                    'text': [info],
                                                    'type': ['image']
                                                    }
                        }
            list_info.append(new_dict)
        else:  # 同一个日期
            list_info[-1]['arr']['link'].append(filename)
            list_info[-1]['arr']['text'].append(info)
            list_info[-1]['arr']['type'].append('image')
    list_info.reverse()  # 翻转
    final_dict = {"list": list_info}
    with open("/Volumes/MAC-WIN/album/data.json", "w") as fp:
        json.dump(final_dict, fp)


def cut_compress():
    src_file_list = list_img_file(SRC_DIR)
    des_file_list = list_img_file(DES_DIR)
    for i in range(len(src_file_list)):
        if src_file_list[i] not in des_file_list:
            Graphics(infile=SRC_DIR + src_file_list[i], outfile=DES_DIR + src_file_list[i]).cut_compress()


def git_operation():
    os.system('git add --all')
    os.system('git commit -m "add photos"')
    os.system('git push origin master')


cut_compress()  # 裁剪图片，裁剪成正方形，去中间部分
git_operation()  # 提交到github仓库
handle_photo()  # 将文件处理成json格式，存到博客仓库中
