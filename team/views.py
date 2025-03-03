from django.shortcuts import render
from django.http import JsonResponse
from .forms import DocumentUploadForm
from .models import Document
from django.forms.models import model_to_dict

from .utils import extract_text_from_pdf, extract_team_info
import logging

logger = logging.getLogger(__name__)

def upload_document(request):
    """Handle file upload, extract team members, and serve the form."""
    
    extracted_team = []  # Store extracted team members

    if request.method == "POST":
        logger.info("Received a POST request for document upload.")
        logger.info(f"Request headers: {request.headers}")
        logger.info(f"Request files: {request.FILES}")

        form = DocumentUploadForm(request.POST, request.FILES)

        if form.is_valid():
            document = form.save()  # Save uploaded file
            extracted_text = extract_text_from_pdf(document.file.path)
            
            if extracted_text:
                extracted_team = extract_team_info(extracted_text)  # Extract team members
                logger.info(f"Final extracted team members: {extracted_team}")
            else:
                logger.warning("No text extracted from the document.")

            # If it's an AJAX request, return JSON instead of rendering HTML
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    "message": f"Document '{document.file.name}' uploaded successfully!",
                    "document": model_to_dict(document),
                    "team_members": extracted_team
                })

            # If not an AJAX request, render the page normally
            return render(request, "team/document_upload.html", {
                "form": form,
                "document": document,
                "team_members": extracted_team
            })
        else:
            logger.error("Form validation failed.")
            logger.error(form.errors.as_json())  # Log detailed errors
            return JsonResponse({"error": "Invalid form data.", "details": form.errors.as_json()}, status=400)

    # Handle GET request by serving the upload form
    logger.info("Serving upload form (GET request)")
    form = DocumentUploadForm()
    return render(request, "team/document_upload.html", {
        "form": form,
        "team_members": extracted_team
    })

def extract_team(request):
    """Extract team information from the latest uploaded document and return as JSON."""
    text = request.session.get("document_text", "")
    if not text:
        return JsonResponse({"error": "No document text found."})

    team_data = extract_team_info(text)
    return JsonResponse({"team": team_data})
