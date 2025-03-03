from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file']  # Ensure only the file field is present

    def clean_file(self):
        """Ensure the uploaded file is not empty and is a valid file."""
        file = self.cleaned_data.get("file", None)
        if not file:
            raise forms.ValidationError("No file was uploaded.")
        return file
