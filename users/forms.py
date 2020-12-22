from django import forms
from . import models


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password1 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = models.User
        fields = ("first_name", "last_name", "email", "password", "password1")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if models.User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already exist.")
        else:
            return email

    def clean_password1(self):
        password = self.cleaned_data.get("password")
        password1 = self.cleaned_data.get("password1")

        if password != password1:
            raise forms.ValidationError("Not matching password.")
        else:
            return password

    def save(self):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password"])
        user.save()


class LogInForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        try:
            user = models.User.objects.get(email=email)
            if user.check_password(password):
                return self.cleaned_data
            else:
                self.add_error("password", forms.ValidationError("Password is wrong."))
        except models.User.DoesNotExist:
            self.add_error("email", forms.ValidationError("User does not exist."))
