from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms
from .models import Stock
#
# class StockForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):                                                        # used to set css classes to the various fields
#         super().__init__(*args, **kwargs)
#         self.fields['name'].widget.attrs.update({'class': 'textinput form-control'})
#         self.fields['quantity'].widget.attrs.update({'class': 'textinput form-control', 'min': '0'})
#
#     class Meta:
#         model = Stock
#         fields = ['name', 'quantity']

# from django import forms
# from .models import Stock
#
# class StockForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['name'].widget.attrs.update({'class': 'textinput form-control'})
#         self.fields['quantity'].widget.attrs.update({'class': 'textinput form-control', 'min': '0'})
#         self.fields['status'].widget = forms.CheckboxInput()  # Explicitly use CheckboxInput for status
#         self.fields['status'].widget.attrs.update({
#             'class': 'form-check-input d-inline-block',  # Use Bootstrap class for checkbox input
#             'style': 'margin-left: 10px; width:20px; height:20px;',  # Custom inline styles
#         })
#
#     class Meta:
#         model = Stock
#         fields = ['name', 'quantity', 'status']

from django import forms
from .models import Stock

class StockForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control', 'min': '0'})
        self.fields['status'].widget = forms.CheckboxInput()  # Explicitly use CheckboxInput for status
        self.fields['status'].widget.attrs.update({
            'class': 'form-check-input d-inline-block',  # Use Bootstrap class for checkbox input
            'style': 'margin-left: 10px; width:20px; height:20px;',  # Custom inline styles
        })

    class Meta:
        model = Stock
        fields = ['name', 'quantity', 'status']


