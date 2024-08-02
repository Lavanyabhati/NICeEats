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
    agent_status = forms.ChoiceField(choices=[('online', 'Online'), ('engaged', 'Engaged'), ('offline', 'Offline')],
                                     required=True, label="Agent Status", initial="offline")
    agent_location_latitude = forms.FloatField(required=True)
    agent_location_longitude = forms.FloatField(required=True)
    verification_status = forms.CharField(max_length=100, required=True, label="Verification Status")

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('agent_location_latitude')
        longitude = cleaned_data.get('agent_location_longitude')

        if (float(latitude) < -90 or float(latitude) > 90):
            self.add_error('agent_location_latitude', f"Latitude must be between -90 and 90 degrees.")

        if (float(longitude) < -90 or float(longitude) > 90):
            self.add_error('agent_location_longitude', f"Longitude must be between -180 and 180 degrees.")

        return self.cleaned_data


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
    agent_location_latitude = forms.FloatField(required=True)
    agent_location_longitude = forms.FloatField(required=True)
    agent_status = forms.ChoiceField(choices=[('online', 'Online'), ('engaged', 'Engaged'), ('offline', 'Offline')],
                                     required=True, label="Agent Status")

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('agent_location_latitude')
        longitude = cleaned_data.get('agent_location_longitude')

        if (float(latitude) < -90 or float(latitude) > 90):
            self.add_error('agent_location_latitude', f"Latitude must be between -90 and 90 degrees.")

        if (float(longitude) < -90 or float(longitude) > 90):
            self.add_error('agent_location_longitude', f"Longitude must be between -180 and 180 degrees.")

        return self.cleaned_data


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
    order_status = forms.ChoiceField(choices=SESSION_STATUS_CHOICES, label='Order Status', required=True)
    # agent_location_latitude = forms.FloatField(required=True)
    # agent_location_longitude = forms.FloatField(required=True)
    payment_mode = forms.ChoiceField(choices=PAYMENT_MODE_CHOICES, label='Payment Mode', required=True)
    payment_amount = forms.IntegerField(label="Payment Amount", required=True)
    # order_id =

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('agent_location_latitude')
        longitude = cleaned_data.get('agent_location_longitude')

        if (float(latitude) < -90 or float(latitude) > 90):
            self.add_error('agent_location_latitude', f"Latitude must be between -90 and 90 degrees.")

        if (float(longitude) < -90 or float(longitude) > 90):
            self.add_error('agent_location_longitude', f"Longitude must be between -180 and 180 degrees.")

        return self.cleaned_data


class UpdateAgentSessionForm(forms.Form):
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
    order_status = forms.ChoiceField(choices=SESSION_STATUS_CHOICES, label='Order Status', required=True)
    agent_location_latitude = forms.FloatField(required=True)
    agent_location_longitude = forms.FloatField(required=True)
    payment_mode = forms.ChoiceField(choices=PAYMENT_MODE_CHOICES, label='Payment Mode', required=True)
    payment_amount = forms.IntegerField(label="Payment Amount", required=True)

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('agent_location_latitude')
        longitude = cleaned_data.get('agent_location_longitude')

        if (float(latitude) < -90 or float(latitude) > 90):
            self.add_error('agent_location_latitude', f"Latitude must be between -90 and 90 degrees.")

        if (float(longitude) < -90 or float(longitude) > 90):
            self.add_error('agent_location_longitude', f"Longitude must be between -180 and 180 degrees.")

        return self.cleaned_data


class AgentProfileStatusForm(forms.Form):
    agent_status = forms.ChoiceField(choices=[('online', 'Online'), ('offline', 'Offline')],
                                     required=True, label="Agent Status")


class UpdateOrderStatusForm(forms.Form):
    order_status = forms.ChoiceField(choices=[('accepted', 'Accepted'), ('picked_up', 'Picked Up'), ('arriving', 'Arriving'), ('reached_location', 'Reached Location'), ('delivered', 'Delivered')],
                                     required=True, label="Agent Status")


class UpdateAgentLocationForm(forms.Form):
    agent_location_latitude = forms.FloatField(required=True)
    agent_location_longitude = forms.FloatField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('agent_location_latitude')
        longitude = cleaned_data.get('agent_location_longitude')

        if (float(latitude) < -90 or float(latitude) > 90):
            self.add_error('agent_location_latitude', f"Latitude must be between -90 and 90 degrees.")

        if (float(longitude) < -90 or float(longitude) > 90):
            self.add_error('agent_location_longitude', f"Longitude must be between -180 and 180 degrees.")

        return self.cleaned_data




# class AddEarningsForm(forms.Form):
#     order_earnings = forms.IntegerField(label="Order Earning", required=True)
#     total_earnings = forms.IntegerField(label="Total Earning", required=True, initial=0)
#
#
# class UpdateEarningsForm(forms.Form):
#     order_earnings = forms.IntegerField(label="Order Earning", required=True)
#     total_earnings = forms.IntegerField(label="Total Earning", required=True, initial=0)