import cv2
import math
from ultralytics import YOLO
import os
import time
from datetime import datetime
from recognition import paddle_ocr
from utils import save_json

cap = cv2.VideoCapture("notebooks\data\car.mp4")

model = YOLO("artifacts/best.pt")

startTime=datetime.now()
license_plates = set()

fps_counter = 0
start_time = time.time()
fps = 0.0  # Initialize fps variable
count = 0
class_name = ['License']

while True:
    ret, frame=cap.read()
    if ret:
        currentTime=datetime.now()
        count += 1
        # print(f"Frame Number : {count}")
        fps_counter += 1
        elapsed_time = time.time() - start_time
        if elapsed_time >= 1.0:
            fps = fps_counter / elapsed_time
            # Reset for the next second
            fps_counter = 0
            start_time = time.time()
        
        # Convert image to rgb since opencv loads images in bgr, if not accuracy will decrease
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Put FPS text on the frame
        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        results=model.predict(frame, conf=0.6)
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                
                class_name_int = int(box.cls[0])
                cls_name=class_name[class_name_int]
                
                conf= math.ceil(box.conf[0]*100)/100
                # label=f'{cls_name}:{conf}'
                plate_region = frame[y1:y2, x1:x2]
                label=paddle_ocr(plate_region)
                
                if label:
                    license_plates.add(label)
                # print("bboxes",x1,x2,y1,y2)
                
                text_size = cv2.getTextSize(label, 0, fontScale=0.5,thickness=2)[0]
                c2 = x1 + text_size[0], y1-text_size[1]-3
                cv2.rectangle(frame, (x1, y1), c2, (255, 0, 0), -1)
                cv2.putText(frame, label,(x1,y1-2),0,0.5,[255,255,255],thickness=1,lineType=cv2.LINE_AA)
        
        if (currentTime-startTime).seconds >= 20:
            endTime=currentTime  
            save_json(license_plates, startTime, endTime) 
            startTime=currentTime
            license_plates.clear()     
        cv2.imshow('Detection', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
         
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    else:
        break  
cap.release()
cv2.destroyAllWindows()