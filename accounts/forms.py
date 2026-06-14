from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CandidateProfile, CompanyProfile, User


class CandidateRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = User.Role.CANDIDATE
        if commit:
            user.save()
        return user


class CompanyRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=200)
    website = forms.URLField(required=False)
    country = forms.CharField(max_length=100, initial="Japan")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = User.Role.COMPANY
        if commit:
            user.save()
            # create the company profile automatically
            CompanyProfile.objects.create(
                user=user,
                name=self.cleaned_data["company_name"],
                website=self.cleaned_data["website"],
                country=self.cleaned_data["country", "Japan"],
            )
        return user


class LoginForm(AuthenticationForm):
    # AuthenticationForm already has username and password fields
    # and handles authentication logic
    # we just inherit it as-is
    pass


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = [
            "bio",
            "resume_url",
            "years_of_experience",
            "skills",
        ]

    def clean_years_of_experience(self):
        years = self.cleaned_data.get("years_of_experience")
        if years and years < 0:
            raise forms.ValidationError("Years of experience cannot be negative.")
        return years


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            "name",
            "description",
            "website",
            "country",
            "founded_year",
        ]

    def clean_founded_year(self):
        year = self.cleaned_data.get("founded_year")
        if year:
            from django.utils import timezone

            current_year = timezone.now().year
            if year < 1800 or year > current_year:
                raise forms.ValidationError(
                    f"Founded year must be between 1800 and {current_year}."
                )
            return year
