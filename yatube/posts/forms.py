from django import forms

from .models import Comment, Post, Profile, User


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

        widgets = {'first_name': forms.TextInput(
            attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(
            attrs={'class': 'form-control'}),
            'email': forms.EmailInput(
            attrs={'class': 'form-control'}),
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'profile_photo', 'instagram', 'bio')

        widgets = {'date_of_birth': forms.DateInput(
            attrs={'class': 'form-control'}),
            'profile_photo': forms.FileInput(
            attrs={'class': 'form-control'}),
            'instagram': forms.TextInput(
            attrs={'class': 'form-control'}),
            'bio': forms.Textarea(
            attrs={'class': 'form-control'}),
        }


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {'text': forms.Textarea(attrs={'class': 'form-control'}),
                   'group': forms.Select(attrs={'class': 'form-control'}),
                   'image': forms.FileInput(attrs={'class': 'form-control'}),
                   }
        help_texts = {'text': 'Текст поста',
                      'group': 'Выберете группу',
                      }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {'text': forms.Textarea(attrs={'class': 'form-control'})}
        labels = {
            'text': 'Текст',
        }
