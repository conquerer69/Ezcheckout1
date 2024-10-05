import cv2
import os
import sys
import signal
import time
from edge_impulse_linux.image import ImageImpulseRunner
import RPi.GPIO as GPIO
from hx711 import HX711
import requests
import json
from requests.structures import CaseInsensitiveDict

class ProductClassifier:
    def __init__(self, model_path):
        self.runner = None
        self.camera = None
        self.id_product = 1
        self.list_label = []
        self.list_weight = []
        self.count = 0
        self.final_weight = 0
        self.taken = 0
        self.ratio = 7.0509  # Set to your calibration ratio
        self.products = {
            'Apple': {'price': 10, 'rate': 0.01},
            'Monaco': {'price': 20, 'rate': 0.02},
            'Lays': {'price': 1, 'rate': 1}
        }
        self.hx = HX711(dout_pin=20, pd_sck_pin=21)
        self.calibrated = False

        GPIO.setmode(GPIO.BCM)
        self.find_weight()

    def find_weight(self):
        if not self.calibrated:
            print('Calibration starts')
            self.hx.zero()
            self.hx.set_scale_ratio(self.ratio)
            self.calibrated = True
            print('Calibration complete')
        time.sleep(1)
        weight = int(self.hx.get_weight_mean(20))
        print(weight, 'g')
        return weight

    def post_product(self, label, final_rate):
        url = "https://ezcheck-71cff480be21.herokuapp.com/product"
        headers = CaseInsensitiveDict({"Content-Type": "application/json"})
        data_dict = {
            "id": self.id_product,
            "name": label,
            "price": self.products[label]['price'],
            "units": "units",
            "taken": self.taken,
            "payable": final_rate
        }
        response = requests.post(url, headers=headers, json=data_dict)
        print(response.status_code)
        self.id_product += 1
        self.list_label.clear()
        self.list_weight.clear()
        self.count = 0
        self.final_weight = 0
        self.taken = 0

    def classify(self):
        # Initialize the camera and model runner
        with ImageImpulseRunner(model_path) as self.runner:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("Couldn't initialize the camera.")
            # Add frame processing and classification logic here

    def run(self):
        self.classify()

def sigint_handler(sig, frame):
    print('Interrupted')
    if runner:
        runner.stop()
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def main(argv):
    if len(argv) == 0:
        print('Usage: python classify.py <path_to_model.eim>')
        sys.exit(2)

    model_path = argv[0]
    classifier = ProductClassifier(model_path)
    classifier.run()

if __name__ == "__main__":
    main(sys.argv[1:])
