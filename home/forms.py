from django import forms
from django.db import models
from cities_light.models import Region, City
from .models import Profile


class ProfileForm(forms.ModelForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.filter(country__code2='US').order_by('name'),
        required=False,
        empty_label='-- Select State --',
        label='State'
    )
    city = forms.IntegerField(
        required=False,
        label='City',
        widget=forms.Select(choices=[('', '-- Select state first --')])
    )

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
            "commute_radius",
            "school_or_job",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.pk:
            if instance.state:
                region = Region.objects.filter(
                    country__code2='US'
                ).filter(
                    models.Q(name__icontains=instance.state)
                    | models.Q(geoname_code__iexact=instance.state)
                ).first()
                if region:
                    self.initial['region'] = region.pk
                    self.fields['city'].choices = [
                        (c.id, c.name) for c in
                        City.objects.filter(region=region).order_by('name')
                    ]
                    if instance.city:
                        city = City.objects.filter(
                            region=region, name__iexact=instance.city
                        ).first()
                        if city:
                            self.initial['city'] = city.id
