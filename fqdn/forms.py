from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import FQDNInstance, KeyWord,Brand



class KeyWordForm(forms.ModelForm):
    #tag = forms.CharField(max_length=128)

    class Meta:
        model = KeyWord
        fields = [

            'tags',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Save Keyword'))

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = [
            
             'tags',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Save Keyword'))
