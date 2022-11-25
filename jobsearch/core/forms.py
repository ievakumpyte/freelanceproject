from django import forms
from .models import Comment, Review

class CommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'rows':'2'}), required=True)

    class Meta:
        model = Comment
        fields = ('body',)


class ReviewForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'rows':'2'}), required=True)

    class Meta:
        model = Review
        fields = ('body',)
