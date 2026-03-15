# forms.py
from django import forms
# forms.py
from django import forms
from .models import BarcodeImage


class FileUploadForm(forms.Form):
    file = forms.FileField()


class BarcodeImageForm(forms.ModelForm):
    class Meta:
        model = BarcodeImage
        fields = ['image']
