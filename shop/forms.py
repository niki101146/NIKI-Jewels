from django import forms

from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [
            "category",
            "name",
            "description",
            "price",
            "gender",
            "material",
            "image",
            "stock",
            "is_available",
            "is_featured",
            "is_new_arrival",
        ]

        widgets = {

            "category": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "placeholder": "Enter product name"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "placeholder": "Enter product description"
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "placeholder": "Enter price",
                    "step": "0.01"
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "material": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "stock": forms.NumberInput(
                attrs={
                    "placeholder": "Enter stock quantity",
                    "min": "0"
                }
            ),
        }

from django import forms
from django.contrib.auth.models import User
from .models import CustomerProfile


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "profile-input",
                "placeholder": "First Name",
            }),

            "last_name": forms.TextInput(attrs={
                "class": "profile-input",
                "placeholder": "Last Name",
            }),

            "email": forms.EmailInput(attrs={
                "class": "profile-input",
                "placeholder": "Email Address",
            }),
        }


class CustomerProfileForm(forms.ModelForm):

    class Meta:
        model = CustomerProfile

        fields = [
            "phone",
            "address",
            "city",
            "state",
            "pincode",
            "country",
            "date_of_birth",
            "gender",
        ]

        widgets = {

            "phone": forms.TextInput(attrs={
                "class": "profile-input",
                "placeholder": "Phone Number",
                "maxlength": "10",
            }),

            "address": forms.Textarea(attrs={
                "class": "profile-input",
                "placeholder": "Enter your complete address",
                "rows": 3,
            }),

            "city": forms.TextInput(attrs={
                "class": "profile-input",
                "placeholder": "City",
            }),

            "state": forms.TextInput(attrs={
                "class": "profile-input",
                "placeholder": "State",
            }),

            "pincode": forms.TextInput(attrs={
                "class": "profile-input",
                "placeholder": "Pincode",
                "maxlength": "10",
            }),

            "country": forms.TextInput(attrs={
                "class": "profile-input",
                "placeholder": "Country",
            }),

            "date_of_birth": forms.DateInput(attrs={
                "class": "profile-input",
                "type": "date",
            }),

            "gender": forms.Select(
                choices=[
                    ("", "Select Gender"),
                    ("Male", "Male"),
                    ("Female", "Female"),
                    ("Other", "Other"),
                ],
                attrs={
                    "class": "profile-input",
                }
            ),
        }


# ============================================================
# REGISTER (customers only - admins are created by the owner)
# ============================================================

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


class RegisterForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
    )

    email = forms.EmailField()

    password1 = forms.CharField(
        widget=forms.PasswordInput,
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput,
    )

    def clean_username(self):

        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")

        return username

    def clean_email(self):

        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean(self):

        cleaned = super().clean()

        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "The two passwords do not match.")

        elif password1:
            try:
                validate_password(
                    password1,
                    user=User(
                        username=cleaned.get("username", ""),
                        email=cleaned.get("email", ""),
                    ),
                )
            except ValidationError as error:
                self.add_error("password1", error)

        return cleaned


class CheckoutCustomerForm(forms.Form):
    name = forms.CharField(label="Full name", max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "name", "placeholder": "Enter your full name"}))
    mobile = forms.CharField(label="Mobile number", max_length=20,
        error_messages={"required": "Please enter a valid mobile number.", "max_length": "Please enter a valid mobile number."},
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel", "inputmode": "tel", "placeholder": "10-digit mobile number"}))
    email = forms.EmailField(label="Email address", max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@example.com"}))

    address = forms.CharField(label="House / street", max_length=300,
        widget=forms.TextInput(attrs={"autocomplete": "address-line1", "placeholder": "House number, building and street"}))
    city = forms.CharField(label="City", max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "address-level2", "placeholder": "City"}))
    state = forms.CharField(label="State", max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "address-level1", "placeholder": "State"}))
    pincode = forms.RegexField(label="PIN code", regex=r"^[1-9][0-9]{5}$", max_length=6,
        error_messages={"invalid": "Enter a valid 6-digit PIN code.", "max_length": "Enter a valid 6-digit PIN code."},
        widget=forms.TextInput(attrs={"autocomplete": "postal-code", "inputmode": "numeric", "placeholder": "6-digit PIN code"}))
    landmark = forms.CharField(label="Landmark (optional)", max_length=200, required=False,
        widget=forms.TextInput(attrs={"placeholder": "Nearby landmark"}))

    def clean_mobile(self):
        import re
        value = re.sub(r"[\s()-]", "", self.cleaned_data["mobile"])
        if value.startswith("+91"):
            value = value[3:]
        if not re.fullmatch(r"[6-9][0-9]{9}", value):
            raise forms.ValidationError("Please enter a valid mobile number. Use 10 digits starting with 6, 7, 8 or 9.")
        return value
