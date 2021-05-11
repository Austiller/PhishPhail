from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import FQDNInstance, KeyWord,Brand



class KeyWordForm(forms.ModelForm):
    class Meta:
        model = KeyWord
        fields = [
            'keyword',
            'tags',
        ]

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = [
            'brand_name',
             'tags',
        ]