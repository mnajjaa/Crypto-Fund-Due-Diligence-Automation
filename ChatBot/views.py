#Upload PDF functionalities
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UploadedDocument


def chatbot_view(request):
    return render(request, 'chatbot.html')
@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf-upload'):
        pdf_file = request.FILES['pdf-upload']
        # Save the uploaded PDF
        document = UploadedDocument(pdf_file=pdf_file)
        document.save()
        # Return the ID of the saved document
        return HttpResponse(str(document.id), status=200)
    return HttpResponse("Invalid request", status=400)

def serve_pdf(request, document_id):
    document = get_object_or_404(UploadedDocument, id=document_id)
    response = FileResponse(document.pdf_file, content_type='application/pdf')
    # Set the Content-Disposition header to inline to encourage rendering in the browser
    response['Content-Disposition'] = 'inline; filename="document.pdf"'
    return response