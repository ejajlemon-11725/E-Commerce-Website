# orders/forms.py
from django import forms

class AddToCartForm(forms.Form):
    qty = forms.IntegerField(min_value=1, initial=1)
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
