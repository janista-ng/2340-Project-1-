from django import forms
from django.db import models
from cities_light.models import Region, City
from .models import Job, Application


class JobForm(forms.ModelForm):
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
        model = Job
        fields = [
            'title', 'company', 'description', 'skills', 'salary',
            'remote', 'visa_sponsorship'
        ]

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


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_note']
