import cv2
import numpy as np
import pytesseract
import pandas as pd

# Point pytesseract to your Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# -----------------------------------------------------------------------------
# IMAGE OCR for legacy tracer **images**
# -----------------------------------------------------------------------------

IMAGE_TABLE_COLUMNS = [
    "No", "Establishment", "Owner", "Address", "Business",
    "Date", "1st", "Date2", "2nd", "Date3", "3rd", "Final", "Remarks"
]

def extract_table_dataframe(image_path: str) -> pd.DataFrame:
    """
    OCR a scanned tracer table image into a DataFrame with
    exactly IMAGE_TABLE_COLUMNS, then drop any footer rows.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

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
            rows.append(current); current = []; last_y = y
        roi = img[y:y+bh, x:x+bw]
        txt = pytesseract.image_to_string(roi, config="--psm 6").strip()
        current.append(txt)
    if current:
        rows.append(current)

    cleaned = [
        row[:len(IMAGE_TABLE_COLUMNS)]
        + [""] * (len(IMAGE_TABLE_COLUMNS) - len(row))
        for row in rows
    ]
    df = pd.DataFrame(cleaned, columns=IMAGE_TABLE_COLUMNS)

    # Drop any footer rows where "No" is empty
    df = df[df["No"].astype(str).str.strip().astype(bool)]
    return df


# -----------------------------------------------------------------------------
# EXCEL OCR for “Monthly Business” sheets ----------------------------
# -----------------------------------------------------------------------------

MONTHLY_COLUMNS = [
    "No", "Name", "Address",
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

def extract_excel_dataframe(file_path: str) -> pd.DataFrame:
    """
    Auto-detect the header row in the first 20 lines for your
    Monthly Business sheets (any business type),
    then return exactly MONTHLY_COLUMNS, dropping any footer rows
    where No is blank.
    """
    preview = (
        pd.read_excel(
            file_path, engine="openpyxl",
            header=None, nrows=20, dtype=str
        )
        .fillna("")
    )

    target = set(c.lower() for c in MONTHLY_COLUMNS)
    header_idx = None
    for i in range(len(preview)):
        row_vals = set(str(v).strip().lower() for v in preview.iloc[i])
        if target.issubset(row_vals):
            header_idx = i
            break
    if header_idx is None:
        header_idx = 0

    df = pd.read_excel(
        file_path, engine="openpyxl",
        skiprows=header_idx, header=0, dtype=str
    )
    df.columns = df.columns.str.strip().str.title()
    for col in MONTHLY_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # Drop any footer rows where "No" is empty
    df = df[df["No"].astype(str).str.strip().astype(bool)]
    return df[MONTHLY_COLUMNS]


# -----------------------------------------------------------------------------
# EXCEL OCR for “Tracer” spreadsheets -----------------------------------
# -----------------------------------------------------------------------------

def extract_tracer_excel_dataframe(file_path: str) -> pd.DataFrame:
    """
    Auto-detect the header row in the first 50 lines for your Tracer Excel,
    map columns into IMAGE_TABLE_COLUMNS, and drop any footer rows.
    """
    preview = (
        pd.read_excel(
            file_path, engine="openpyxl",
            header=None, nrows=50, dtype=str
        )
        .fillna("")
    )

    required = {
        "no.", "name establishment", "name of owner",
        "name/business", "remarks"
    }
    header_idx = None
    for i in range(len(preview)):
        row = set(str(v).strip().lower() for v in preview.iloc[i])
        if required.issubset(row):
            header_idx = i
            break
    if header_idx is None:
        header_idx = 0

    df = pd.read_excel(
        file_path, engine="openpyxl",
        skiprows=header_idx, header=0, dtype=str
    )

    # Strip whitespace on column names
    df.columns = df.columns.str.strip()

    # Remap to IMAGE_TABLE_COLUMNS
    new_cols = []
    date_counter = 0
    for col in df.columns:
        low = col.lower()
        if low in ("no.", "no"):
            new_cols.append("No")
        elif low == "name establishment":
            new_cols.append("Establishment")
        elif low == "name of owner":
            new_cols.append("Owner")
        elif low == "address":
            new_cols.append("Address")
        elif low in ("name/business", "name business"):
            new_cols.append("Business")
        elif low == "1st":
            new_cols.append("1st")
        elif low == "2nd":
            new_cols.append("2nd")
        elif low == "3rd":
            new_cols.append("3rd")
        elif low == "final":
            new_cols.append("Final")
        elif low == "remarks":
            new_cols.append("Remarks")
        elif low == "date":
            date_counter += 1
            new_cols.append(
                ["Date", "Date2", "Date3"][min(date_counter - 1, 2)]
            )
        else:
            new_cols.append(col.title())  # will be dropped later

    df.columns = new_cols

    for col in IMAGE_TABLE_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # Drop any footer rows where "No" is empty
    df = df[df["No"].astype(str).str.strip().astype(bool)]

    # Return exactly the 13 tracer columns
    return df[IMAGE_TABLE_COLUMNS]
