from django import forms
from .models import MovieRequest, MoviePetition

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


class MoviePetitionForm(forms.ModelForm):
    class Meta:
        model = MoviePetition
        fields = ["name", "description"]
        labels = {
            "name": "Movie Name",
            "description": "Why should this movie be added?",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control", "placeholder": "Tell us why this movie should be added to our catalog..."}),
        }