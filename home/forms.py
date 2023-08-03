from django import forms
from .models import Post, Comment


class PostSearchForm(forms.Form):
    search = forms.CharField()



class PostCreateUpdateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('body',)
        widgets = {
            'body':forms.Textarea(attrs={'class':'form-control'})
        }


class CommentCreationForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'class':'form-control'})
        }


class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


