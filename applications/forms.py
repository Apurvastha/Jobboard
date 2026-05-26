from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):

    class Meta:
        model = Application
        fields = ['cover_letter']

    def clean_cover_letter(self):
        cover_letter = self.cleaned_data.get('cover_letter')
        if cover_letter and len(cover_letter) < 50:
            raise forms.ValidationError(
                'Cover letter must be at least 50 characters.'
            )
        return cover_letter