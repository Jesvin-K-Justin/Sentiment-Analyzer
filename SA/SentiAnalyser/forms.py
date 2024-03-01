# forms.py
from django import forms
from .models import AnalyzerData

class AnalyzerForm(forms.ModelForm):
    class Meta:
        model = AnalyzerData
        fields = ['content_name', 'content_description', 'video_url', 'uploaded_file']
        widgets = {
            'content_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'content_description': forms.Textarea(attrs={'class': 'form-control', 'required': True}),
            'video_url': forms.TextInput(attrs={'class': 'form-control'}),
            'uploaded_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
