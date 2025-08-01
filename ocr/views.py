import os
import pandas as pd

from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .utils import (
    extract_table_dataframe,
    extract_excel_dataframe,
    extract_tracer_excel_dataframe,
)
from .services import save_ocr_records  # ← import your save helper

class OCRParseView(APIView):
    """
    POST under key 'file' either:

    • A scanned image of your tracer table → returns rows with columns:
        No, Establishment, Owner, Address, Business,
        Date, 1st, Date2, 2nd, Date3, 3rd, Final, Remarks

    • A “Tracer” Excel sheet (auto-detects header row) → same 13 tracer columns

    • A “Monthly Business” Excel sheet (auto-detects header row)
      → returns rows with columns:
        No, Name, Address,
        January, …, December
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        upload = request.FILES.get('file')
        if not upload:
            return Response(
                {"error": "No file provided under 'file' key."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1) Save upload to a temp location
        tmp_name = default_storage.save(f"tmp/{upload.name}", upload)
        tmp_path = default_storage.path(tmp_name)

        try:
            ext = os.path.splitext(upload.name)[1].lower()

            if ext in (".xls", ".xlsx"):
                # --- Peek at first 50 rows (no header) to detect which format ---
                preview = (
                    pd.read_excel(
                        tmp_path,
                        engine="openpyxl",
                        header=None,
                        nrows=50,
                        dtype=str
                    )
                    .fillna("")
                )

                tracer_header = {"no.", "name establishment", "name of owner", "name/business", "remarks"}
                is_tracer = any(
                    tracer_header.issubset({str(cell).strip().lower() for cell in row})
                    for _, row in preview.iterrows()
                )

                if is_tracer:
                    df = extract_tracer_excel_dataframe(tmp_path)
                else:
                    df = extract_excel_dataframe(tmp_path)
            else:
                # Image → fixed 13 tracer-record columns
                df = extract_table_dataframe(tmp_path)

            # Sanitize for JSON
            df = df.fillna("").astype(str)

            # Persist parsed rows into the database
            save_ocr_records(df, ext)

            # Return JSON
            return Response(df.to_dict(orient="records"))

        except Exception as e:
            print(f"OCRParseView failed for {upload.name!r}: {e!r}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:
            default_storage.delete(tmp_name)
