from django import forms
from .models import MovieRequest

class MovieRequestForm(forms.ModelForm):
    class Meta:
        model = MovieRequest
        fields = ["name", "description"]
        labels = {
            "name": "Movie Name",
            "description": "Movie Description",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }