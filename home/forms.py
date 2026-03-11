from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "show_contact_email",
            "show_contact_phone",
            "show_location",
            "show_school_or_job",
            "show_about_me",
            "show_skills",
            "show_education",
            "show_work_experience",
            "show_links",
            "display_name",
            "headline",
            "school_or_job",
            "location",
            "profile_image",
            "about_me",
            "skills",
            "education",
            "work_experience",
            "linkedin_url",
            "github_url",
            "portfolio_url",
            "contact_email",
            "contact_phone",
        ]
        widgets = {
            "display_name": forms.TextInput(attrs={"type": "text"}),
            "headline": forms.TextInput(attrs={"type": "text", "placeholder": "Ex: GT student seeking SWE internship"}),
            "school_or_job": forms.TextInput(attrs={"type": "text"}),
            "location": forms.TextInput(attrs={"type": "text"}),
            "about_me": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Write something about yourself..."
            }),
            "skills": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Ex: Python, Django, Java, SQL, Git..."
            }),
            "education": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Ex: Georgia Tech — BS Computer Science (Expected 2027)..."
            }),
            "work_experience": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Ex: Software Intern — Company (Dates)\n- Bullet point\n- Bullet point"
            }),
            "linkedin_url": forms.URLInput(attrs={"placeholder": "https://linkedin.com/in/yourname"}),
            "github_url": forms.URLInput(attrs={"placeholder": "https://github.com/yourname"}),
            "portfolio_url": forms.URLInput(attrs={"placeholder": "https://yourportfolio.com"}),
            "contact_email": forms.EmailInput(attrs={"placeholder": "name@email.com"}),
            "contact_phone": forms.TextInput(attrs={"placeholder": "(123) 456-7890"}),
        }
