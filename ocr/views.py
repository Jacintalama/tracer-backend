from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from django.core.files.storage import default_storage
from .utils import extract_table_dataframe

class OCRParseView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        img_file = request.FILES.get('file')
        if not img_file:
            return Response(
                {"error": "No file provided under 'file' key."},
                status=status.HTTP_400_BAD_REQUEST
            )

        tmp_path = default_storage.save(f"tmp/{img_file.name}", img_file)
        try:
            df = extract_table_dataframe(default_storage.path(tmp_path))
            data = df.to_dict(orient="records")
            return Response(data)
        except Exception as e:
            print("Table OCR error:", repr(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            default_storage.delete(tmp_path)
