import numpy as np
import re
import os
from paddleocr import PaddleOCR
import logging
# Suppress PaddleOCR logging
logging.getLogger('ppocr').setLevel(logging.WARNING)

ocr = PaddleOCR(use_angle_cls = True, use_gpu = False)

def paddle_ocr(plate_region):
    result = ocr.ocr(plate_region, det=False, rec=True,cls=False)
    text = ""
    for r in result:
        scores = r[0][1]
        
        if np.isnan(scores):
            scores = 0
        else:
            scores = int(scores*100)
            
        if scores > 60:
            text = r[0][0]
            
    pattern = re.compile('[\W]')
    text = pattern.sub("", text)
    text = text.replace("???", "")
    text = text.replace("0", "0")
    text = text.replace("粤", "")
    return str(text)