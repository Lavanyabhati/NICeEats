from django import forms
from django.core.exceptions import ValidationError


class RegisterDeliveryAgentForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Name")
    mobile_number = forms.CharField(max_length=10, required=True, label="Mobile Number",
                                        widget=forms.TextInput(attrs={'type': 'number'}))
    address = forms.CharField(max_length=255, required=True, label="Address")
    email = forms.EmailField(max_length=100, required=True, label="Email")
    date_of_birth = forms.DateField(required=True, label="Date of Birth",
                                    widget=forms.TextInput(attrs={'type': 'date'}), help_text="Use the format YYYY-MM-DD")
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], required=True,
                                   label="Gender")
    verification_id = forms.CharField(max_length=100, required=True, label="Verification ID")
    verification_type = forms.CharField(max_length=100, required=True, label="Verification Type")
    vehicle_type = forms.CharField(max_length=100, required=True, label="Verification Type")
    vehicle_reg_no = forms.CharField(max_length=100, required=True, label="Vehicle Registration Number")
    agent_status = forms.CharField(max_length=100, required=True, label="Agent Status")


class UpdateDeliveryAgentForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Name")
    address = forms.CharField(max_length=255, required=True, label="Address")
    email = forms.EmailField(max_length=100, required=True, label="Email")
    date_of_birth = forms.DateField(required=True, label="Date of Birth",
                                    widget=forms.TextInput(attrs={'type': 'date'}), help_text="Use the format YYYY-MM-DD")
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], required=True,
                                   label="Gender")
    verification_id = forms.CharField(max_length=100, required=True, label="Verification ID")
    verification_type = forms.CharField(max_length=100, required=True, label="Verification Type")
    vehicle_type = forms.CharField(max_length=100, required=True, label="Verification Type")
    vehicle_reg_no = forms.CharField(max_length=100, required=True, label="Vehicle Registration Number")
    agent_status = forms.CharField(max_length=100, required=True, label="Agent Status")


class AgentSessionForm(forms.Form):
    SESSION_STATUS_CHOICES = [
            ('accepted', 'Accepted'),
            ('picked_up', 'Picked Up'),
            ('arriving', 'Arriving'),
            ('reached_location', 'Reached Location'),
            ('delivered', 'Delivered'),
    ]

    PAYMENT_MODE_CHOICES = [
            ('cash', 'Cash'),
            ('card', 'Card'),
            ('online', 'Online'),
    ]

    session_start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label='Session Start Time')
    session_end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label='Session End Time')
    order_status = forms.ChoiceField(choices=SESSION_STATUS_CHOICES, label='Order Status')
    agent_location_latitude = forms.CharField(max_length=100)
    agent_location_longitude = forms.CharField(max_length=100)
    payment_mode = forms.ChoiceField(choices=PAYMENT_MODE_CHOICES, label='Payment Mode')
    payment_amount = forms.IntegerField(label="Payment Amount")

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')

        if (float(latitude) < -90 or float(latitude) > 90):
            self.add_error('latitude', f"Latitude must be between -90 and 90 degrees.")

        if (float(longitude) < -90 or float(longitude) > 90):
            self.add_error('longitude', f"Longitude must be between -180 and 180 degrees.")






# class AddEarningsForm(forms.Form):
#     order_earnings = forms.IntegerField(label="Order Earning", required=True)
#     total_earnings = forms.IntegerField(label="Total Earning", required=True, initial=0)
#
#
# class UpdateEarningsForm(forms.Form):
#     order_earnings = forms.IntegerField(label="Order Earning", required=True)
#     total_earnings = forms.IntegerField(label="Total Earning", required=True, initial=0)