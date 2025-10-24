from ultralytics import YOLO
from dotenv import load_dotenv
import os
import cv2
from PIL import Image
load_dotenv()
weights_path = os.getenv("YOLO_WEIGHTS")

class WidgetDetector:
    def __init__(self, device='cpu'):
        self.YOLO_weights = weights_path
        self.device = device
        self.last_detections = None
        self.last_annotations = None
        self.last_orig_img = None
        self.model = YOLO(self.YOLO_weights)

    def predict(self, image, confidence_threshold=0.5, iou_threshold=0.3):
        results = self.model.predict(source=image,
                                     conf=confidence_threshold,
                                     device=self.device,
                                     iou=iou_threshold)
        self.last_orig_img = image
        self.last_detections = {}
        self.last_orig_img = results[0].orig_img.copy()

        for r in results:
            for idx, box in enumerate(r.boxes):
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                x_min, y_min = x1, y1
                width, height = int(x2-x1), int(y2-y1)
                self.last_detections[idx] = {
                    'bounding_box': [x_min, y_min, width, height],
                    'conf': float(box.conf)
                }
        return self.last_detections

    def attach_bounding_boxes(self):
        if self.last_detections is None:
            raise Exception('No prediction has been made or no widgets have been detected')
        img = self.last_orig_img.copy()
        for det_id, det in self.last_detections.items():
            x_min, y_min, w, h = det['bounding_box']
            x1, y1, x2, y2 = int(x_min), int(y_min), int(x_min + w), int(y_min + h)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(img, str(det_id), (x1-20, (y1 + y2) // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(img_rgb)
        return pil