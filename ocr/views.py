import os
import pandas as pd

from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .utils import (
    extract_table_dataframe,
    extract_tracer_excel_dataframe,
)


@method_decorator(csrf_exempt, name='dispatch')
class OCRParseView(APIView):
    """
    POST under key 'file' either:

    • A scanned image → returns rows with columns:
        No, Establishment, Owner, Address, Business,
        Date, 1st, Date2, 2nd, Date3, 3rd, DateFinal, Final, Remarks

    • A “Tracer” Excel sheet → same columns above
    """

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        upload = request.FILES.get("file")
        if not upload:
            return Response(
                {"error": "No file provided under 'file' key."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tmp_name = default_storage.save(f"tmp/{upload.name}", upload)
        tmp_path = default_storage.path(tmp_name)

        try:
            ext = os.path.splitext(upload.name)[1].lower()

            # IMAGE OCR
            if ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
                df = extract_table_dataframe(tmp_path)

            # EXCEL OCR
            elif ext in (".xls", ".xlsx"):
                preview = (
                    pd.read_excel(
                        tmp_path,
                        engine="openpyxl",
                        header=None,
                        nrows=50,
                        dtype=str,
                    ).fillna("")
                )

                tracer_keywords = {
                    "no", "establishment", "owner", "address", "business", "remarks"
                }

                def normalize(cell):
                    return str(cell).strip().lower().replace(".", "")

                is_tracer = False
                for _, row in preview.iterrows():
                    normalized_row = {normalize(cell) for cell in row}
                    matched = tracer_keywords.intersection(normalized_row)
                    if len(matched) >= 3:
                        is_tracer = True
                        break

                if is_tracer:
                    df = extract_tracer_excel_dataframe(tmp_path)
                else:
                    return Response(
                        {"error": "Unrecognized Excel format. Only Tracer sheets are supported."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            else:
                return Response(
                    {"error": f"Unsupported file type: '{ext}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            df = df.fillna("").astype(str)
            return Response(df.to_dict(orient="records"), status=status.HTTP_200_OK)

        except Exception as e:
            print(f"OCRParseView failed for {upload.name!r}: {e!r}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        finally:
            default_storage.delete(tmp_name)
