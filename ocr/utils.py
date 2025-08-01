# tracer_backend/ocr/utils.py

import cv2
import numpy as np
import pytesseract
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_table_dataframe(image_path):
    # 1. Load & preprocess
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 2. Find lines
    h, w = binary.shape
    vert_k = cv2.getStructuringElement(cv2.MORPH_RECT, (1, h//50))
    horiz_k = cv2.getStructuringElement(cv2.MORPH_RECT, (w//50, 1))
    vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vert_k)
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horiz_k)

    # 3. Get grid contours
    grid = cv2.add(vertical, horizontal)
    cnts, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(c) for c in cnts if cv2.contourArea(c) > 1000]
    boxes = sorted(boxes, key=lambda b: (b[1]//50, b[0]))

    # 4. OCR each cell
    cols = ["No", "Establishment", "Owner", "Address", "Business",
            "Date", "1st", "Date2", "2nd", "Date3", "3rd", "Final", "Remarks"]
    rows, current, last_y = [], [], boxes[0][1]
    for x,y,w,h in boxes:
        if abs(y - last_y) > h//2:
            rows.append(current); current=[]; last_y=y
        roi = img[y:y+h, x:x+w]
        text = pytesseract.image_to_string(roi, config="--psm 6").strip()
        current.append(text)
    if current: rows.append(current)

    # 5. Build DataFrame
    cleaned = [r[:len(cols)] + [""]*(len(cols)-len(r)) for r in rows]
    return pd.DataFrame(cleaned, columns=cols)
