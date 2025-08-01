from django.http import HttpResponse
import pytesseract

def home(request):
    return HttpResponse("Welcome to Tracer Backend!")
