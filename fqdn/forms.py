from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import FQDNInstance, KeyWord,Brand, SquatedWord



class KeyWordForm(forms.ModelForm):
    #tag = forms.CharField(max_length=128)

    class Meta:
        model = KeyWord
        fields = [
            'keyword',
            'tags',
        ]

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Save Keyword'))

    @property
    def slug_name(self):
        return 'keyword'
class KeywordUpdate(forms.ModelForm):
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
    @property
    def slug_name(self):
        return 'keyword'

class BrandUpdate(forms.ModelForm):
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
    @property
    def slug_name(self):
        return 'brand_name'

class SquatedWordForm(forms.ModelForm):
    class Meta:
        model = SquatedWord
        fields = [
             'squated_word',
             'tags',
        ]




    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Save SquatedWord'))
    
    @property
    def slug_name(self):
        return 'squated_word'


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = [
             'brand_name',
             'tags',
        ]
    


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Save Brand'))

