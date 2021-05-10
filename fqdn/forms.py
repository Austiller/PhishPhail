from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import FQDNInstance, KeyWord,Brand

class KeyWordForm (forms.ModelForm):
    """
    
    Using the Django Form helper to build a form for the model showing the details of the model currently running. 
    
    
    """
  

    
    
    class Meta:
        model = KeyWord
        fields = ('keyword','keyword_tags')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        

        
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Save'))