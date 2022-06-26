import os
import math
import datetime

import cv2
import numpy as np
from PIL import Image

from detection.yolov5_detector import Detector
from rotation.deskew import determine_skew, rotate
from rotation.rotation_skorch import PassportRotation

import Levenshtein
from scipy.spatial.distance import cdist
from paddleocr import PaddleOCR

from mrz.checker.td3 import TD3CodeChecker


detector = Detector()
detector.load("./detection/weights/passport_yolov5s.pt")
rotator = PassportRotation()
ocr = PaddleOCR(lang="en")


def detect_passport(path):
    det_result = detector.detect_bbox(path)
    return det_result[0]

def rotate_passport(image):
    grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    deskew_angle = determine_skew(grayscale)
    image = rotate(image, deskew_angle, (0, 0, 0))
    rotation_angle = rotator.predict(image) 
    if rotation_angle == 90:
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    if rotation_angle == 180:
        image = cv2.rotate(image, cv2.ROTATE_180)
    if rotation_angle == 270:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return image

def ocr_passport(path):
    return ocr.ocr(path)

def detect_mrz(image, ocr_result):
    height, width, _ = image.shape
    y_roi = int(height * 4/5)
    mrz = []
    for line in ocr_result:
        coords, word = line
        word = word[0].replace(" ", "")
        p_list = []
        if len(word) >= 40:
            for p in coords:
                if p[1] >= y_roi:
                    p_list += [True]
                else:
                    p_list += [False]
            if all(p_list):
                if len(word) == 44:
                    mrz += [word]
                else:
                    mrz += [word.ljust(44, "<")]
    return "\n".join(mrz).upper()

def parse_mrz(mrz):
    td3_check = TD3CodeChecker(mrz)
    fields = td3_check.fields()
    passport_serial = "".join(filter(str.isalpha, fields.document_number))
    passport_number = "".join(filter(str.isdigit, fields.document_number))
    if int(fields.birth_date[0:2]) < (datetime.datetime.now().year - 2000):
        year_prefix = "20"
    else:
        year_prefix = "19"
    birth_date = f"{fields.birth_date[4:6]}.{fields.birth_date[2:4]}.{year_prefix}{fields.birth_date[0:2]}"
    expiry_date = f"{fields.expiry_date[4:6]}.{fields.expiry_date[2:4]}.20{fields.expiry_date[0:2]}"
    return {"GIVEN NAMES": fields.name,
            "SURNAME": fields.surname,
            "SEX": fields.sex,
            "SERIAL": passport_serial,
            "NUMBER": passport_number, 
            "DATE OF BIRTH": birth_date,
            "DATE OF EXPIRY": expiry_date,
            "PINFL": fields.optional_data,
            "VALID": str(bool(td3_check)).upper()}

def bbox_centers(coords):
    x_center = (coords[0][0] + coords[2][0]) / 2
    y_center = (coords[0][1] + coords[2][1]) / 2
    return [int(x_center), int(y_center)]

def calc_distance(line1, line2):
    line1_segs = np.array(list(zip(np.linspace(line1[0][0], line2[1][0], 100, dtype=int),
                np.linspace(line1[0][1], line1[1][1], 100, dtype=int))))
    line2_segs = np.array(list(zip(np.linspace(line2[0][0], line2[1][0], 100, dtype=int),
                np.linspace(line2[0][1], line2[1][1], 100, dtype=int))))
    avg_distance = np.average(cdist(list(line1_segs), list(line2_segs)).min(axis=1))
    return avg_distance

def dot(v1, v2):
    return v1[0]*v2[0]+v1[1]*v2[1]

def calc_direction(line1, line2):
    v1 = [(line1[0][0] - line1[1][0]), (line1[0][1] - line1[1][1])]
    v2 = [(line2[0][0] - line2[1][0]), (line2[0][1] - line2[1][1])]
    dot_prod = dot(v1, v2)
    mag1 = dot(v1, v1)**0.5
    mag2 = dot(v2, v2)**0.5
    try:
        angle = math.acos(dot_prod / (mag1 * mag2))
        angle = math.degrees(angle) % 360
        if angle - 180 >= 0:
            return 360 - angle
        else:
            return angle
    except:
        return 0

def process_passport(image, ocr_result, mrz_items):
    keys_dict = {}
    values_dict = {}
    dates = []
    for line in ocr_result:
        coords, word = line
        word = word[0].upper()
        if word.replace(" ", "").isdigit():
            dates += [word.replace(" ", "")]
        word_center = bbox_centers(coords)
        with open("./utils/fields_dict.txt", "r") as fp:
            for field in fp.readlines():
                field = field.rstrip("\n")
                if Levenshtein.distance(field, word) <= 3 and field not in keys_dict.keys():
                    keys_dict[field] = {"coords": coords, "center": word_center}
                elif Levenshtein.distance(field, word) > 3 and word not in values_dict.keys() and field not in keys_dict.keys():
                    values_dict[word] = {"coords": coords, "center": word_center}
    new_values_dict = {}
    for k, v in values_dict.items():
        if v["center"] not in [i["center"] for i in keys_dict.values()]:
            new_values_dict[k] = v

    height, width, _ = image.shape
    req_dist =  height / 30
    key_value_dict = {}
    for key_word, key_items in keys_dict.items():
        for value_word, value_items in new_values_dict.items():
            key_word_botom_line = [key_items["coords"][3], key_items["coords"][2]]
            value_word_top_line = [value_items["coords"][0], value_items["coords"][1]]
            act_dist = calc_distance(key_word_botom_line, value_word_top_line)
            
            init_line = [key_items["coords"][3], value_items["coords"][0]]
            init_direction = calc_direction(key_word_botom_line, init_line)
            center_line1 = [[key_items["coords"][0][0], key_items["center"][1]], key_items["center"]]
            center_line2 = [key_items["center"], value_items["center"]]
            center_direction = calc_direction(center_line1, center_line2)
            avg_direction = (init_direction + center_direction) / 2

            if (act_dist > 0 and act_dist <= req_dist and act_dist != 13) and (avg_direction >= 0 and avg_direction <= 100):      
                if key_word not in key_value_dict.keys():
                    key_value_dict[key_word] = [value_word]
                else:
                    key_value_dict[key_word] += [value_word]

    if "KIM TOMONIDAN BERILGAN" in key_value_dict.keys():
        with open("./utils/iib.txt", "r") as fp:
            for iib in fp.readlines():
                iib = iib.rstrip("\n")
                if Levenshtein.distance(iib, " ".join(key_value_dict["KIM TOMONIDAN BERILGAN"])) <= 3:
                    mrz_items["GIVEN BY"] = iib
    
    for date in [d[:2]+"."+d[2:4]+"."+d[4:] for d in dates]:
        try:
            real_date = datetime.datetime.strptime(date, "%d.%m.%Y").year
            if int(real_date) > int(mrz_items["DATE OF BIRTH"].split(".")[2]) \
                and int(real_date) < int(mrz_items["DATE OF EXPIRY"].split(".")[2]):
                if date not in [mrz_items["DATE OF BIRTH"], mrz_items["DATE OF EXPIRY"]]:
                    mrz_items["DATE OF ISSUE"] = date
        except:
            continue
    return mrz_items