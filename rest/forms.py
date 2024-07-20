from django import forms
from django.core.exceptions import ValidationError


class RegisterRestaurantForm(forms.Form):
    name = forms.CharField(max_length=100)
    location_name = forms.CharField(max_length=255)
    category = forms.CharField(max_length=255)
    latitude = forms.CharField(max_length=100)
    longitude = forms.CharField(max_length=100)
    food_type = forms.ChoiceField(choices=[('veg', 'Vegetarian'), ('non-veg', 'Non-Vegetarian'), ('veg/non-veg', 'Veg/Non-Veg')])
    operating_hours = forms.CharField(widget=forms.Textarea)
    subcategory = forms.CharField(widget=forms.Textarea, help_text="Enter each subcategory separated by a comma.")

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        subcategory = cleaned_data.get('subcategory')

        if (float(latitude) < -90 or float(latitude) > 90):
            self.add_error('latitude', f"Latitude must be between -90 and 90 degrees.")

        if (float(longitude) < -90 or float(longitude) > 90):
            self.add_error('longitude', f"Longitude must be between -180 and 180 degrees.")

        if subcategory:
            subcategory_list = [sub.strip() for sub in subcategory.split(',') if sub.strip()]
            cleaned_data['subcategory'] = subcategory_list

        return self.cleaned_data


class RestaurantListForm(forms.Form):
    latitude = forms.FloatField(required=True)
    longitude = forms.FloatField(required=True)
    max_distance = forms.FloatField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        max_distance = cleaned_data.get('max_distance')

        if (float(latitude) < -90 or float(latitude) > 90):
            self.add_error('latitude', f"Latitude must be between -90 and 90 degrees.")

        if (float(longitude) < -90 or float(longitude) > 90):
            self.add_error('longitude', f"Longitude must be between -180 and 180 degrees.")

        return self.cleaned_data


class RestaurantUpdateForm(forms.Form):
    name = forms.CharField(max_length=100)
    location_name = forms.CharField(max_length=255)
    category = forms.CharField(max_length=255)
    latitude = forms.CharField(max_length=100)
    longitude = forms.CharField(max_length=100)
    food_type = forms.ChoiceField(choices=[('veg', 'Vegetarian'), ('non-veg', 'Non-Vegetarian'), ('veg/non-veg', 'Veg/Non-Veg')])
    operating_hours = forms.CharField(widget=forms.Textarea)
    subcategory = forms.CharField(widget=forms.Textarea, help_text="Enter each subcategory separated by a comma.")

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        subcategory = cleaned_data.get('subcategory')

        if (float(latitude) < -90 or float(latitude) > 90):
            self.add_error('latitude', f"Latitude must be between -90 and 90 degrees.")

        if (float(longitude) < -90 or float(longitude) > 90):
            self.add_error('longitude', f"Longitude must be between -180 and 180 degrees.")

        if subcategory:
            subcategory_list = [sub.strip() for sub in subcategory.split(',') if sub.strip()]
            cleaned_data['subcategory'] = subcategory_list


class RegisterRestaurantOwnerForm(forms.Form):
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


class UpdateRestaurantOwnerForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Name")
    address = forms.CharField(max_length=255, required=True, label="Address")
    email = forms.EmailField(max_length=100, required=True, label="Email")
    date_of_birth = forms.DateField(required=True, label="Date of Birth",
                                    widget=forms.TextInput(attrs={'type': 'date'}), help_text="Use the format YYYY-MM-DD")
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], required=True,
                                   label="Gender")
    verification_id = forms.CharField(max_length=100, required=True, label="Verification ID")
    verification_type = forms.CharField(max_length=100, required=True, label="Verification Type")


class MenuForm(forms.Form):
    item_name = forms.CharField(max_length=100)
    item_description = forms.CharField(widget=forms.Textarea)
    item_price = forms.DecimalField(max_digits=10, decimal_places=2)
    item_type = forms.ChoiceField(choices=[('Veg', 'Veg'), ('Non-Veg', 'Non-Veg')])
    item_category = forms.ChoiceField()

    def __init__(self, *args, subcategory_list=None, **kwargs):
        super(MenuForm, self).__init__(*args, **kwargs)
        if subcategory_list:
            self.fields['item_category'].choices = [(cat.strip(), cat.strip()) for cat in subcategory_list if
                                                    cat.strip()]


class MenuUpdateForm(forms.Form):
    item_name = forms.CharField(max_length=100)
    item_description = forms.CharField(widget=forms.Textarea)
    item_price = forms.DecimalField(max_digits=10, decimal_places=2)
    item_type = forms.ChoiceField(choices=[('Veg', 'Veg'), ('Non-Veg', 'Non-Veg')])
    item_category = forms.ChoiceField()

    def __init__(self, *args, subcategory_list=None, **kwargs):
        super(MenuUpdateForm, self).__init__(*args, **kwargs)
        if subcategory_list:
            self.fields['item_category'].choices = [(cat.strip(), cat.strip()) for cat in subcategory_list if
                                                    cat.strip()]


class RateItemForm(forms.Form):
    item_rating = forms.FloatField(label='Item Rating',min_value=0.0, max_value=5.0, required=True)


class UpdateRatingForm(forms.Form):
    old_rating = forms.FloatField(label='Old Rating',min_value=0.0, max_value=5.0, required=True)
    new_rating = forms.FloatField(label='New Rating',min_value=0.0, max_value=5.0, required=True)