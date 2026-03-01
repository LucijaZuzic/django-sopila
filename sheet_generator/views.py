import os
from sheet_generator.apps import APP_DIR
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, \
    HttpResponseNotAllowed, HttpResponseServerError, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sheet_generator.utils import ToneParser, make_prediction_file
from .forms import UploadFileForm
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def download_sheet_api(request, filename):

    try:
        logger.info("Prediction successfully started.")
        make_prediction_file(filename)
        logger.info("Prediction successfully created.")
        
        sheet = ToneParser(filename)
        sheet.parse_tones()
        
        pdf_dir = os.path.join(APP_DIR, 'pdf')
        if not os.path.isdir(pdf_dir):
            logger.info(f"Making a pdf directory: {pdf_dir}")
            os.makedirs(pdf_dir)

        pdf_path = os.path.join(APP_DIR, 'pdf', filename + '.pdf')
        if not os.path.exists(pdf_path):
            return HttpResponseServerError("PDF generation failed.")

        return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=f"{filename}.pdf")
    except Exception as e:
        logger.error(f"Error processing sheet: {str(e)}")
        return HttpResponseServerError(f"Internal Error: {e}")

@csrf_exempt
def upload_recording_api(request):

    if request.method != 'POST':
        logger.warning("Only POST here")
        return HttpResponseNotAllowed(['POST'])

    form = UploadFileForm(request.POST, request.FILES)
    if not form.is_valid():
        logger.warning("Invalid form submission to upload_recording_api")
        return HttpResponseServerError("Invalid call")

    #  Saving POST'ed file to storage
    file = request.FILES['audio']
    file_name = default_storage.save(file.name, file)
    logger.info(f"File uploaded successfully: {file_name}")
    return HttpResponse('OK')
