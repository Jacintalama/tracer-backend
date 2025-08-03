import cv2
import numpy as np
import pytesseract
import pandas as pd

# Point pytesseract to your Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# -----------------------------------------------------------------------------
# IMAGE OCR for legacy tracer **images**
# -----------------------------------------------------------------------------

IMAGE_TABLE_COLUMNS = [
    "No", "Establishment", "Owner", "Address", "Business",
    "Date", "1st", "Date2", "2nd", "Date3", "3rd",
    "DateFinal", "Final", "Remarks"
]

def extract_table_dataframe(image_path: str) -> pd.DataFrame:
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    h, w = binary.shape
    vert_k = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(1, h // 50)))
    horiz_k = cv2.getStructuringElement(cv2.MORPH_RECT, (max(1, w // 50), 1))
    vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vert_k)
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horiz_k)
    grid = cv2.add(vertical, horizontal)

    cnts, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    boxes = [cv2.boundingRect(c) for c in cnts if cv2.contourArea(c) > 500]
    if not boxes:
        return pd.DataFrame([], columns=IMAGE_TABLE_COLUMNS)

    boxes.sort(key=lambda b: (b[1], b[0]))

    rows, current, last_y = [], [], boxes[0][1]
    for x, y, bw, bh in boxes:
        if abs(y - last_y) > bh // 2:
            rows.append(current)
            current = []
            last_y = y
        roi = img[y:y+bh, x:x+bw]
        txt = pytesseract.image_to_string(roi, config="--psm 6").strip()
        current.append(txt)
    if current:
        rows.append(current)

    cleaned = [
        row[:len(IMAGE_TABLE_COLUMNS)] + ["" for _ in range(len(IMAGE_TABLE_COLUMNS) - len(row))]
        for row in rows
    ]
    df = pd.DataFrame(cleaned, columns=IMAGE_TABLE_COLUMNS)
    df = df[df["No"].astype(str).str.strip().astype(bool)]
    return df

# -----------------------------------------------------------------------------
# EXCEL OCR for "Tracer" spreadsheets only
# -----------------------------------------------------------------------------

def extract_tracer_excel_dataframe(file_path: str) -> pd.DataFrame:
    preview = (
        pd.read_excel(file_path, engine="openpyxl", header=None, nrows=50, dtype=str)
        .fillna("")
    )

    required = {
        "no", "establishment", "owner", "address", "business", "remarks"
    }

    def normalize(cell):
        return str(cell).strip().lower().replace(".", "")

    header_idx = None
    for i in range(len(preview)):
        row = set(normalize(cell) for cell in preview.iloc[i])
        if len(required.intersection(row)) >= 3:
            header_idx = i
            break
    if header_idx is None:
        header_idx = 0

    df = pd.read_excel(
        file_path, engine="openpyxl",
        skiprows=header_idx, header=0, dtype=str
    )
    df.columns = df.columns.str.strip()

    date_names = ["Date", "Date2", "Date3", "DateFinal"]
    new_cols = []
    date_counter = 0

    for col in df.columns:
        low = col.strip().lower().replace(".", "")
        if low == "no":
            new_cols.append("No")
        elif low == "establishment":
            new_cols.append("Establishment")
        elif low == "owner":
            new_cols.append("Owner")
        elif low == "address":
            new_cols.append("Address")
        elif low == "business":
            new_cols.append("Business")
        elif low == "1st":
            new_cols.append("1st")
        elif low == "2nd":
            new_cols.append("2nd")
        elif low == "3rd":
            new_cols.append("3rd")
        elif low == "remarks":
            new_cols.append("Remarks")
        elif "date" in low:
            new_cols.append(date_names[min(date_counter, len(date_names) - 1)])
            date_counter += 1
        elif low == "final":
            new_cols.append("Final")
        else:
            new_cols.append(col.title())

    df.columns = new_cols

    for col in IMAGE_TABLE_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[df["No"].astype(str).str.strip().astype(bool)]
    return df[IMAGE_TABLE_COLUMNS]
