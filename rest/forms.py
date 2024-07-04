from django import forms


class RegisterRestaurantForm(forms.Form):
    name = forms.CharField(max_length=100)
    location_name = forms.CharField(max_length=255)
    category = forms.CharField(max_length=255)
    latitude = forms.CharField(max_length=100)
    longitude = forms.CharField(max_length=100)


class RestaurantListForm(forms.Form):
    name = forms.CharField(max_length=100)
    location = forms.CharField(max_length=255)

class RestaurantUpdateForm(forms.Form):
    name = forms.CharField(max_length=100)
    location = forms.CharField(max_length=255)
    coordinates = forms.CharField(max_length=100)

class RegisterRestaurantOwnerForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Name")
    mobile_number = forms.CharField(max_length=10, required=True, label="Mobile Number",
                                        widget=forms.TextInput(attrs={'type': 'number'}))
    address = forms.CharField(max_length=255, required=True, label="Address")
    email = forms.EmailField(max_length=100, required=True, label="Email")
    age = forms.IntegerField(min_value=0, required=True, label="Age",
                                 widget=forms.TextInput(attrs={'type': 'number'}))
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], required=True,
                                   label="Gender")
    verification_id = forms.CharField(max_length=100, required=True, label="Verification ID")
    verification_type = forms.CharField(max_length=100, required=True, label="Verification Type")


