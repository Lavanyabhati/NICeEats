from django import forms
from django.contrib.auth.models import User
from django import forms


class UserForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    age = forms.IntegerField()
    address = forms.CharField(max_length=255)


class OwnerForm(forms.Form):
    address = forms.CharField(max_length=255)
    email = forms.EmailField()
    age = forms.IntegerField()


#
# class ProfileForm(forms.Form):
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email', 'age', 'address', 'phone_number']
#
#     first_name = forms.CharField(max_length=255)
#     last_name = forms.CharField(max_length=255)
#     email = forms.CharField(max_length=255)
#     age = forms.CharField(max_length=255)
#     address = forms.CharField(max_length=255)
#     phone_number = forms.CharField(max_length=255)
#
#     def clean_phone_number(self):
#         phone_number = self.cleaned_data['phone_number']
#         if not phone_number.isDigit():
#             raise forms.ValidationError('Phone number must contain only digits')
#         return phone_number
#
#     def clean_age(self):
#         age = self.cleaned_data['age']
#         if age < 100:
#             raise forms.ValidationError('Age should be less than 100')
#         return age
#
#
