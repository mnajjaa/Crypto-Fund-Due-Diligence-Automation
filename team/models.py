from django.db import models

class Document(models.Model):
    file = models.FileField(upload_to='documents/', max_length=255)  # Increase max_length
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def title(self):
        """Generate a title automatically from the filename (without extension)."""
        return self.file.name.rsplit('/', 1)[-1].split('.')[0]

    def __str__(self):
        return self.title
