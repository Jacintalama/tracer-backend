from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import pandas as pd
import os

from ocr.utils import (
    extract_table_dataframe,
    extract_tracer_excel_dataframe,
)


@csrf_exempt
def home(request):
    if request.method == "POST" and request.FILES.get("file"):
        upload = request.FILES["file"]
        ext = os.path.splitext(upload.name)[1].lower()
        tmp_path = f"tmp_{upload.name}"

        with open(tmp_path, "wb") as f:
            for chunk in upload.chunks():
                f.write(chunk)

        try:
            if ext in (".xls", ".xlsx"):
                preview = pd.read_excel(tmp_path, header=None, nrows=50, dtype=str).fillna("")

                tracer_keywords = {"no", "establishment", "owner", "address", "business", "remarks"}

                def normalize(cell):
                    return str(cell).strip().lower().replace(".", "")

                is_tracer = False
                for _, row in preview.iterrows():
                    normalized = {normalize(cell) for cell in row}
                    if len(tracer_keywords.intersection(normalized)) >= 3:
                        is_tracer = True
                        break

                print("Detected format:", "Tracer" if is_tracer else "Unsupported")

                if is_tracer:
                    df = extract_tracer_excel_dataframe(tmp_path)
                else:
                    return HttpResponse("Unsupported Excel format. Only Tracer sheets are allowed.", status=400)

            elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
                df = extract_table_dataframe(tmp_path)

            else:
                return HttpResponse(f"Unsupported file type: {ext}", status=400)

            return render(request, "upload_result.html", {
                "table_html": df.fillna("").to_html(classes="table table-bordered", index=False),
                "filename": upload.name
            })

        except Exception as e:
            return HttpResponse(f"Error processing file: {e}", status=500)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    return render(request, "upload_form.html")
