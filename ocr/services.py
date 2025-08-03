from .models import TracerRecord  # Replace with your actual model name

def save_ocr_records(df, ext):
    """
    Save parsed OCR/excel data to the database.

    Args:
        df (pd.DataFrame): cleaned DataFrame from OCR or Excel
        ext (str): file extension (.xlsx, .jpg, etc.)
    """
    for _, row in df.iterrows():
        TracerRecord.objects.create(
            no=row.get("No", ""),
            establishment=row.get("Establishment", ""),
            owner=row.get("Owner", ""),
            address=row.get("Address", ""),
            business=row.get("Business", ""),
            date=row.get("Date", ""),
            first=row.get("1st", ""),
            date2=row.get("Date2", ""),
            second=row.get("2nd", ""),
            date3=row.get("Date3", ""),
            third=row.get("3rd", ""),
            datefinal=row.get("DateFinal", ""),   # ← new field
            final=row.get("Final", ""),
            remarks=row.get("Remarks", ""),
        )
