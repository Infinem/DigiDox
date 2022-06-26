import math
import numpy as np
import yaml
import cv2
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)


def read_yaml(path):
    with open(path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            return exc


def rule_based_ocr(path, doc_type):
    result = ocr.ocr(path, cls=True)
    image = cv2.imread(path)
    print(result)
    rule = read_yaml(f"./rules/{doc_type}.yaml")
    word_centers = {}
    for item in result:
        word = item[1][0]
        coords = item[0]

        # color = [int(clr) for clr in rule[word]["color"].replace(" ", "").split(",")]
        xmin = int(min([p[0] for p in coords]))
        xmax = int(max([p[0] for p in coords]))
        ymin = int(min([p[1] for p in coords]))
        ymax = int(max([p[1] for p in coords]))
        
        x_center = (xmax - xmin) / 2
        y_center = (ymax - ymin) / 2
        word_centers[word] = {"coords": [[xmin, ymax], [xmax, ymin]], "center": [x_center, y_center]}

        cv2.rectangle(image, (xmin, ymax), (xmax, ymin), (255, 0, 0), 2)
        cv2.putText(image, word, (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.5, (0, 0, 255), 2, cv2.LINE_AA)
    for word1, points1 in word_centers.items():
        if word1 in rule:
            for word2, points2 in word_centers.items():
                slope, intercept = np.polyfit(points1["center"], points2["center"], 1)
                angle_in_degrees = math.degrees(math.atan(slope))
                # print(word1, intercept, angle_in_degrees, word2)
                if rule[word1]["data-direction"] == "bottom" and angle_in_degrees > 62 and angle_in_degrees < 66:
                    distance = np.linalg.norm(np.array(points1["center"]) - np.array(points2["center"]))
                    if distance > int(rule[word1]["min-distance"]) and distance < int(rule[word1]["max-distance"]):
                        print(word1, distance, word2)
        
    cv2.imwrite("./tmp/result.jpg", image)
    return None