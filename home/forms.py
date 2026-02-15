from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "display_name",
            "school_or_job",
            "location",
            "profile_image",
            "about_me",
            "contact_email",
            "contact_phone",
        ]
        widgets = {
            "display_name": forms.TextInput(attrs={"type": "text"}),
            "school_or_job": forms.TextInput(attrs={"type": "text"}),
            "location": forms.TextInput(attrs={"type": "text"}),
            "about_me": forms.Textarea(attrs={"rows": 5, "placeholder": "Write something about yourself..."}),
        }