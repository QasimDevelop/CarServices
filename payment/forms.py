from datetime import datetime, timedelta
from django import forms
from .models import ShippingAddress

from django import forms

class RestrictedDateInput(forms.DateInput):
    input_type = 'date'  # Crucial: Set input_type to 'date'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format = '%Y-%m-%d'  # Important for consistent formatting
        self.attrs['min'] = (datetime.now().date()).strftime('%Y-%m-%d')
        self.attrs['max'] = (datetime.now().date() + timedelta(days=7)).strftime('%Y-%m-%d')


class SlotSelectForm(forms.Form):
    slot_date = forms.DateField(
        label='Select Date',
        widget=RestrictedDateInput(attrs={'class': 'form_select'}),
        required=True,
    )
    
    slot_time = forms.ChoiceField(
        label='Select Slot Time',
        widget=forms.Select(attrs={'class': 'form_select'}),
        required=True,
        choices=[],  # Will be populated in __init__
    )
    
    # Image field for visual representation of the fault
    image = forms.ImageField(
        label='Upload Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose an image for your report (optional)'
        })
    )
    
    # Description field with a Textarea widget
    description = forms.CharField(
        label='Description',
        required=False,  # Set to True if this field is mandatory
        widget=forms.Textarea(attrs={
            'rows': 4,  # Adjust rows as needed
            'cols': 50,  # Adjust columns as needed
            'maxlength': 100,  # Limit to about 100 words
            'placeholder': 'Provide a brief description (up to 100 words).',
            'class': 'form-control',
        }),
    )

    def __init__(self, *args, **kwargs):
        slots = kwargs.pop('slots', [])
        super(SlotSelectForm, self).__init__(*args, **kwargs)
        
        # Generate date choices
        today = datetime.now().date()
        max_date = today + timedelta(days=7)
        
        # Update the date field to use a Select widget with available dates
        self.fields['slot_date'] = forms.DateField(
            label='Select Date',
            widget=forms.Select(
                choices=[
                    (date.strftime('%Y-%m-%d'), date.strftime('%Y-%m-%d'))
                    for date in self.get_available_dates(today, max_date)
                ],
                attrs={'class': 'form_select'}
            ),
            initial=today.strftime('%Y-%m-%d'),
            required=True,
        )
        
        # Prepare time slot choices
        choices = []
        for index, s in enumerate(slots):
            if s.start_time:
                formatted_time = s.start_time.strftime("%I:%M %p")
                # Store the actual slot ID instead of index for better reliability
                choices.append((s.id, formatted_time))
            else:
                choices.append((str(index), 'No Time Available'))
        
        # Add an empty option if the field is not required
        if not self.fields['slot_time'].required:
            choices.insert(0, ('', '---------'))
            
        self.fields['slot_time'].choices = choices

    def get_available_dates(self, min_date, max_date):
        """Generates a list of dates between min_date and max_date (inclusive)."""
        available_dates = []
        current_date = min_date
        while current_date <= max_date:
            available_dates.append(current_date)
            current_date += timedelta(days=1)
        return available_dates

    

class ShippingForm(forms.ModelForm):
	shipping_full_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Full Name'}), required=True)
	shipping_email = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}), required=True)
	shipping_address1 = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Address1'}), required=True)
	shipping_address2 = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Address2'}), required=False)
	shipping_city = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'City'}), required=True)
	shipping_state = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'State'}), required=False)
	shipping_zipcode = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Zipcode'}), required=False)
	shipping_country = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Country'}), required=True)
	class Meta:
		model = ShippingAddress
		fields = ['shipping_full_name', 'shipping_email', 'shipping_address1', 'shipping_address2', 'shipping_city', 'shipping_state', 'shipping_zipcode', 'shipping_country']

		exclude = ['user',]


class PaymentForm(forms.Form):
	card_name =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Name On Card'}), required=True)
	card_number =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Card Number'}), required=True)
	card_exp_date =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Expiration Date'}), required=True)
	card_cvv_number =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'CVV Code'}), required=True)
	card_address1 =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Billing Address 1'}), required=True)
	card_address2 =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Billing Address 2'}), required=False)
	card_city =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Billing City'}), required=True)
	card_state = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Billing State'}), required=True)
	card_zipcode =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Billing Zipcode'}), required=True)
	card_country =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Billing Country'}), required=True)
