from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from trainer.models import Model, FQDNInstance


class ModelForm(forms.ModelForm):
    """Using the Django Form helper to build a form for the model"""

    def clean_model_name(self):
        """Santize the user input for the model name."""
        name = self.cleaned_data['model_name']
        #Add Description Field.
        return name

    class Meta:
        model = Model
        fields = ('model_name','model_version', 'model_description','set_as_default')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
    
        #self.helper.fields['accuracy_training_set'].widget.attrs['readyonly'] = True
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Save Model'))

class FQDNInstanceForm (forms.ModelForm):   
    
    fqdn_type = forms.TypedChoiceField(
        choices = (('Malicious', "Malicious"),('Likely Malicious', "Likely Malicious"),  ("Likely Bengin", "Likely Benign"),("Benign", "Benign")),
        widget = forms.Select,
        initial = 'Malicious',
        required = True,
    )

    class Meta: 
        model = FQDNInstance
        
        fields = ('fqdn_type',)
    def __init__ (self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Save FQDN'))
       

  

