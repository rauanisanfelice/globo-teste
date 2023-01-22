from django import forms


class UploadFileForm(forms.Form):

    file = forms.FileField(
        label="Arquivo", help_text="Importe o arquivo de formato csv"
    )
