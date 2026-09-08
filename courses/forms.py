from django import forms
from .models import Lesson




class LessonForm(forms.ModelForm):

    class Meta:
        model = Lesson

        fields = [
            'title',
            'content',
        ]

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Lesson title'
                }
            ),

            'content': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 8,
                    'placeholder': 'Lesson content'
                }
            ),
        }