# import os
# import json
# import numpy as np
# json_dir = r"C:\Users\stone\Desktop\data\stamp\json"
# txt_dir = r"C:\Users\stone\Desktop\data\stamp\txt"
# json_list = os.listdir(json_dir)
#
# for index, file in enumerate(json_list):
#     json_name = os.path.join(json_dir, file)
#     txt_name  = os.path.join(txt_dir, file.split(".")[0] + ".txt")
#     txt_list = []
#     with open(json_name) as json_file:
#         load_dict = json.load(json_file)
#         for point in load_dict['shapes']:
#             txt_ = np.array(point['points']).reshape((-1,1))
#             txt_ = np.squeeze(txt_)
#             txt_ = [str(x) for x in txt_]
#             txt = ",".join(txt_) + "\n"
#             txt_list.append(txt)
#
#     with open(txt_name, "w") as txt_file:
#         for file in txt_list:
#             txt_file.writelines(file)

# -*- coding=utf-8 -*-
#!/usr/bin/python

import sys
import os
import shutil
import numpy as np
import json
import cv2
import xml.etree.ElementTree as ET

# 检测框的ID起始值
START_BOUNDING_BOX_ID = 1
# 类别列表无必要预先创建，程序中会根据所有图像中包含的ID来创建并更新
PRE_DEFINE_CATEGORIES = {}
# If necessary, pre-define category and its id
#  PRE_DEFINE_CATEGORIES = {"aeroplane": 1, "bicycle": 2, "bird": 3, "boat": 4,
                         #  "bottle":5, "bus": 6, "car": 7, "cat": 8, "chair": 9,
                         #  "cow": 10, "diningtable": 11, "dog": 12, "horse": 13,
                         #  "motorbike": 14, "person": 15, "pottedplant": 16,
                         #  "sheep": 17, "sofa": 18, "train": 19, "tvmonitor": 20}


def get(root, name):
    vars = root.findall(name)
    return vars


def get_and_check(root, name, length):
    vars = root.findall(name)
    if len(vars) == 0:
        raise NotImplementedError('Can not find %s in %s.'%(name, root.tag))
    if length > 0 and len(vars) != length:
        raise NotImplementedError('The size of %s is supposed to be %d, but is %d.'%(name, length, len(vars)))
    if length == 1:
        vars = vars[0]
    return vars


# 得到图片唯一标识号
def get_filename_as_int(filename):
    try:
        filename = os.path.splitext(filename)[0]
        return int(filename)
    except:
        raise NotImplementedError('Filename %s is supposed to be an integer.'%(filename))


def convert(xml_list, xml_dir, json_file):
    '''
    :param xml_list: 需要转换的XML文件列表
    :param xml_dir: XML的存储文件夹
    :param json_file: 导出json文件的路径
    :return: None
    '''
    list_fp = xml_list
    # 标注基本结构
    json_dict = {"images":[],
                 "type": "instances",
                 "annotations": [],
                 "categories": []}
    categories = PRE_DEFINE_CATEGORIES
    bnd_id = START_BOUNDING_BOX_ID
    for line in list_fp:
        line = line.strip()
        print("buddy~ Processing {}".format(line))
        # 解析XML
        xml_f = os.path.join(xml_dir, line)
        tree = ET.parse(xml_f)
        root = tree.getroot()
        path = get(root, 'path')
        # 取出图片名字
        if len(path) == 1:
            filename = os.path.basename(path[0].text)
        elif len(path) == 0:
            filename = get_and_check(root, 'filename', 1).text
        else:
            raise NotImplementedError('%d paths found in %s'%(len(path), line))
        ## The filename must be a number
        image_id = get_filename_as_int(filename)  # 图片ID
        size = get_and_check(root, 'size', 1)
        # 图片的基本信息
        width = int(get_and_check(size, 'width', 1).text)
        height = int(get_and_check(size, 'height', 1).text)
        image = {'file_name': filename,
                 'height': height,
                 'width': width,
                 'id':image_id}
        json_dict['images'].append(image)
        ## Cruuently we do not support segmentation
        #  segmented = get_and_check(root, 'segmented', 1).text
        #  assert segmented == '0'
        # 处理每个标注的检测框
        for obj in get(root, 'object'):
            # 取出检测框类别名称
            category = get_and_check(obj, 'name', 1).text
            # 更新类别ID字典
            if category not in categories:
                new_id = len(categories)
                categories[category] = new_id
            category_id = categories[category]
            bndbox = get_and_check(obj, 'bndbox', 1)
            xmin = int(get_and_check(bndbox, 'xmin', 1).text) - 1
            ymin = int(get_and_check(bndbox, 'ymin', 1).text) - 1
            xmax = int(get_and_check(bndbox, 'xmax', 1).text)
            ymax = int(get_and_check(bndbox, 'ymax', 1).text)
            assert (xmax > xmin)
            assert (ymax > ymin)
            annotation = dict()
            annotation['area'] = o_width*o_height
            annotation['iscrowd'] = 0
            annotation['image_id'] = image_id
            annotation['bbox'] = [xmin, ymin, o_width, o_height]
            annotation['category_id'] = category_id
            annotation['id'] = bnd_id
            annotation['ignore'] = 0
            # 设置分割数据，点的顺序为逆时针方向
            annotation['segmentation'] = [[xmin,ymin,xmin,ymax,xmax,ymax,xmax,ymin]]

            json_dict['annotations'].append(annotation)
            bnd_id = bnd_id + 1

    # 写入类别ID字典
    for cate, cid in categories.items():
        cat = {'supercategory': 'none', 'id': cid, 'name': cate}
        json_dict['categories'].append(cat)
    # 导出到json
    json_fp = open(json_file, 'w')
    json_str = json.dumps(json_dict)
    json_fp.write(json_str)
    json_fp.close()

def txt_convert(txt_list, txt_dir,img_dir, json_file):
    '''
    :param txt_list: 需要转换的txt文件列表
    :param txt_dir: txt的存储文件夹
    :param img_dir: IMG的存储文件夹
    :param json_file: 导出json文件的路径
    :return: None
    '''
    list_fp = txt_list
    # 标注基本结构
    json_dict = {"images": [],
                 "type": "instances",
                 "annotations": [],
                 "categories": []}
    categories = PRE_DEFINE_CATEGORIES
    bnd_id = START_BOUNDING_BOX_ID
    for line in list_fp:
        line = line.strip()
        print("buddy~ Processing {}".format(line))
        # 解析txt
        txt_f = os.path.join(txt_dir, line)
        img_f = os.path.join(img_dir, line.split(".")[0] + ".jpg")
        filename = line.split(".")[0] + ".jpg"
        ## The filename must be a number
        image_id = get_filename_as_int(filename)  # 图片ID
        height, width = cv2.imread(img_f).shape[:-1]
        # 图片的基本信息

        image = {'file_name': filename,
                 'height': height,
                 'width': width,
                 'id':image_id}
        json_dict['images'].append(image)
        ## Cruuently we do not support segmentation
        #  segmented = get_and_check(root, 'segmented', 1).text
        #  assert segmented == '0'
        # 处理每个标注的检测框
        with open(txt_f, "r") as f:
            txt_lines = f.readlines()
            for obj in txt_lines:
                # 取出检测框类别名称
                category = "1"
                # 更新类别ID字典
                if category not in categories:
                    new_id = len(categories)
                    categories[category] = new_id
                category_id = categories[category]
                bndbox = obj.split(",")
                xmin = int(float(bndbox[0].strip())) - 1
                ymin = int(float(bndbox[1].strip())) - 1
                xmax = int(float(bndbox[2].strip()))
                ymax = int(float(bndbox[3].strip()))
                if xmax < xmin:
                    xmax, xmin = xmin, xmax
                if ymax < ymin:
                    ymax, ymin = ymin, ymax
                o_width = abs(xmax - xmin)
                o_height = abs(ymax - ymin)
                annotation = dict()
                annotation['area'] = o_width*o_height
                annotation['iscrowd'] = 0
                annotation['image_id'] = image_id
                annotation['bbox'] = [xmin, ymin, o_width, o_height]
                annotation['category_id'] = category_id
                annotation['id'] = bnd_id
                annotation['ignore'] = 0
                # 设置分割数据，点的顺序为逆时针方向
                annotation['segmentation'] = [[xmin,ymin,xmin,ymax,xmax,ymax,xmax,ymin]]

                json_dict['annotations'].append(annotation)
                bnd_id = bnd_id + 1

    # 写入类别ID字典
    for cate, cid in categories.items():
        cat = {'supercategory': 'none', 'id': cid, 'name': cate}
        json_dict['categories'].append(cat)
    # 导出到json
    json_fp = open(json_file, 'w')
    json_str = json.dumps(json_dict)
    json_fp.write(json_str)
    json_fp.close()


if __name__ == '__main__':
    # root_path = os.getcwd()
    xml_path = r"C:\Users\stone\Desktop\data\stamp"
    xml_dir = os.path.join(xml_path, 'txt')
    jpg_dir = os.path.join(xml_path, 'JPEGImages')
    xml_labels = os.listdir(os.path.join(xml_path, 'txt'))
    np.random.shuffle(xml_labels)
    split_point = int(len(xml_labels)/10)

    # validation data
    xml_list = xml_labels[0:split_point]
    json_file = os.path.join(xml_path, 'stamp_val2014.json')

    txt_convert(xml_list, xml_dir, jpg_dir, json_file)
    for xml_file in xml_list:
        img_name = xml_file[:-4] + '.jpg'
        shutil.copy(os.path.join(xml_path, 'JPEGImages', img_name),
                    os.path.join(xml_path, 'val2014', img_name))
    # train data
    xml_list = xml_labels[split_point:]
    json_file = os.path.join(xml_path, 'instances_train2014.json')
    txt_convert(xml_list, xml_dir, jpg_dir, json_file)
    for xml_file in xml_list:
        img_name = xml_file[:-4] + '.jpg'
        shutil.copy(os.path.join(xml_path, 'JPEGImages', img_name),
                    os.path.join(xml_path, 'train2014', img_name))


