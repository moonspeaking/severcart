from django import forms
from accounts.models import AnconUser

class RegistrationForm(forms.ModelForm):
    """
    Form for registering a new account.
    """
    username = forms.CharField(widget=forms.TextInput, label="Логин")
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label="Пароль")
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Повторите пароль")

    required_css_class = 'required'


    class Meta:
        model = AnconUser
        fields = ['username', 'password1', 'password2', 'last_name', 'first_name', 'patronymic', 'department']

    def clean(self):
        """
        Verifies that the values entered into the password fields match

        NOTE: Errors here will appear in ``non_field_errors()`` because it applies to more than one field.
        """
        self.cleaned_data = super(RegistrationForm, self).clean()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Пароли не совпадаю. Введите их повторно.")
        return self.cleaned_data

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user