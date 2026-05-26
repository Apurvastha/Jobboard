from django import forms
from . models import JobListing, Category


class JobSearchForm(forms.Form):
    search = forms.CharField(max_length=200, required=False)
    location = forms.CharField(max_length=100, required=False)
    job_type = forms.ChoiceField(
        choices=[('', 'All')] + JobListing.JobType.choices,
        required=False
    )
    experience_level = forms.ChoiceField(
        choices=[('', 'All')] + JobListing.ExperienceLevel.choices,
        required=False
    )
    salary_min = forms.IntegerField(required=False, min_value=0)
    salary_max = forms.IntegerField(required=False, min_value=0)
    is_remote = forms.BooleanField(required=False)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')

        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError(
                'Maximum salary should be greater than minimum salary'
            )
        return cleaned_data
    

class JobListingForm(forms.ModelForm):

    class Meta:
        model = JobListing
        fields = [
            'title',
            'description',
            'category',
            'job_type',
            'experience_level',
            'location',
            'is_remote',
            'salary_min',
            'salary_max',
            'deadline',
            'tags',
        ]
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise forms.ValidationError(
                'Title must be at least 10 characters.'
            )
        return title.strip()
    
    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        if salary_min and salary_max and salary_max <= salary_min:
            raise forms.ValidationError(
                'Maximum salary must be greater than minimum salary.'
            )
        return cleaned_data




