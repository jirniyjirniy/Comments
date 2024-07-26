import django.forms as forms

from comment.models import Comment


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        # Настройка виджетов для полей
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ваше имя'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ваш email'})
        self.fields['homepage'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ваш сайт (опционально)'})
        self.fields['message'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Ваше сообщение', 'rows': 4})

    class Meta:
        model = Comment
        fields = ['username', 'email', 'homepage', 'message', 'parent', 'image', 'text_file']
        widgets = {
            'parent': forms.HiddenInput(),
        }
