from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from trainer.models import Model


class ModelForm(forms.ModelForm):
    """Using the Django Form helper to build a form for the model"""

    def clean_model_name(self):
        """Santize the user input for the model name."""
        name = self.cleaned_data['model_name']
        #Add Description Field.
        return name

    class Meta:
        model = Model
        fields = ('model_name', 'model_description','set_as_default')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
    

        #self.helper.fields['accuracy_training_set'].widget.attrs['readyonly'] = True
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Save Model'))


#Need Create StopModel form twith functionality with a shared base form. 

class ModelDetails(forms.ModelForm):
    """
    
    Using the Django Form helper to build a form for the model showing the details of the model currently running. 
    
    
    """
    read_only_fields = ['model_running', 'model_algorithm','accuracy_precision','accuracy_recall','accuracy_training_set']


    def clean_model_name(self):
        """Santize the user input for the model name."""
        name = self.cleaned_data['model_name']
        
        return name
    
    

    class Meta:
        model = Model
 
        fields = ('model_name','model_description','model_algorithm','set_as_default', 'accuracy_training_set', 'accuracy_precision','accuracy_recall')



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        
  
        for field in self.fields:
            self.fields[field].widget.attrs['readonly'] = True
            
        
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Edit'))

class ModelEdit(forms.ModelForm):
    """
    
    Using the Django Form helper to build a form for the model showing the details of the model currently running. 
    
    
    """
    read_only_fields = ['model_algorithm','accuracy_precision','accuracy_recall','accuracy_training_set']


    def clean_model_name(self):
        """Santize the user input for the model name."""
        name = self.cleaned_data['model_name']
        
        return name
    
    

    class Meta:
        model = Model
 
        fields = ('model_name','model_algorithm','set_as_default', 'accuracy_training_set', 'accuracy_precision','accuracy_recall')



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        
        #Set fields to be read_only so form appearance aligns with functionality of the form. 

        for field in self.read_only_fields:
            self.fields[field].widget.attrs['readonly'] = True
            
        
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Save'))



