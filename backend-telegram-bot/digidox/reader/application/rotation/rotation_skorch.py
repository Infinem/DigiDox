import time
import logging
logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s - %(message)s")

import torch
import torchvision
from skorch import NeuralNetClassifier

import albumentations
from albumentations import pytorch

from reader.application.rotation.resnet18 import ResNet18


class PassportRotation():
    def __init__(self):
        self.label_list = [0, 90, 180, 270]
        self.transforms = albumentations.Compose([
            albumentations.Resize(416, 416),
            albumentations.Normalize([0.485, 0.456, 0.406],
                                    [0.229, 0.224, 0.225]),
            pytorch.ToTensorV2()
            ])

        self.resnet = NeuralNetClassifier(
            module=ResNet18(4),          
            criterion=torch.nn.CrossEntropyLoss,
            device="cpu"
            )
        self.resnet.initialize()
        self.resnet.load_params(f_params="./reader/application/rotation/weights/rotation_resnet18.pkl")

    def predict(self, image):
        start_time = time.perf_counter()
        image = self.transforms(image=image)["image"]
        prediction = self.resnet.predict(image.unsqueeze(0))
        end_time = time.perf_counter()
        logging.info("Result: {0}".format(self.label_list[prediction[0]]))
        logging.info("Done in {:.2f} seconds".format(end_time - start_time))
        return self.label_list[prediction[0]]