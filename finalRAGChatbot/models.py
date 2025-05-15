from django.db import models

# Create your models here.
from django.db import models

class UploadedDocument(models.Model):
    pdf_file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PDF uploaded at {self.uploaded_at}"