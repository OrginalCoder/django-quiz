from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class UzbekUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Elektron pochta",
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "placeholder": "namuna@mail.uz",
            "autocomplete": "email"
        })
    )

    class Meta:
        model = User
        fields = ("username", "email")
        labels = {
            "username": "Foydalanuvchi nomi",
        }
        help_texts = {
            "username": "Faqat lotin harflari, raqamlar va @/./+/-/_ belgilari.",
        }
        error_messages = {
            "username": {
                "unique": "Bu foydalanuvchi nomi allaqachon band. Boshqa nom tanlang.",
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "django_master",
            "autocomplete": "username"
        })
        if "password1" in self.fields:
            self.fields["password1"].label = "Parol"
            self.fields["password1"].widget.attrs.update({
                "class": "form-input",
                "placeholder": "Kamida 6 ta belgi",
                "autocomplete": "new-password"
            })
            self.fields["password1"].help_text = "Parol kamida 6 ta belgidan iborat bo'lishi kerak."
        if "password2" in self.fields:
            self.fields["password2"].label = "Parolni tasdiqlang"
            self.fields["password2"].widget.attrs.update({
                "class": "form-input",
                "placeholder": "Parolni qayta kiriting",
                "autocomplete": "new-password"
            })
            self.fields["password2"].help_text = "Yuqoridagi parol bilan bir xil bo'lishi shart."

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ushbu elektron pochta bilan ro'yxatdan o'tilgan.")
        return email


class UzbekAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Foydalanuvchi nomi"
        self.fields["username"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "Foydalanuvchi nomingiz",
            "autocomplete": "username"
        })
        self.fields["password"].label = "Parol"
        self.fields["password"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "Parolingiz",
            "autocomplete": "current-password"
        })
        self.error_messages["invalid_login"] = "Foydalanuvchi nomi yoki parol noto'g'ri kiritildi."
        self.error_messages["inactive"] = "Ushbu hisob faol emas."
