from django import forms


class SubscribeForm(forms.Form):
    email = forms.EmailField(label='Adres e-mail', max_length=200)
