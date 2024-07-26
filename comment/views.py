from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView

from comment.forms import CommentForm
from comment.models import Comment

from django.http import JsonResponse


class CommentView(View):
    """Представлени комментариев"""

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = CommentForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    form_instance = form.save(commit=False)
                    if request.POST.get('parent', None):
                        form_instance.parent_id = int(request.POST.get('parent'))
                    form_instance.save()
                    return JsonResponse({'status': 'success', 'message': 'Комментарий успешно добавлен.'})
                except ValidationError as e:
                    errors = [error for error in e.messages]
                    return JsonResponse({'status': 'error', 'errors': errors})
            else:
                errors = {field: form.errors[field] for field in form.errors}
                return JsonResponse({'status': 'error', 'errors': errors})
        return JsonResponse({'status': 'error', 'message': 'Некорректный запрос'})


class CommentListView(ListView):
    model = Comment
    template_name = 'comment.html'
    paginate_by = 3

    def get_queryset(self):
        order_by = self.request.GET.get('order_by', '-date').strip()
        valid_sort_fields = ['date', '-date', 'username', '-username', 'email', '-email']
        if order_by not in valid_sort_fields:
            order_by = '-date'
        return Comment.objects.filter(parent__isnull=True).order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_filtered = self.request.GET.get('filter', 'false') == 'true'
        context['is_filtered'] = is_filtered
        context['form'] = CommentForm()
        current_sort = self.request.GET.get('order_by', '-date')
        context['current_sort'] = current_sort.strip()
        return context

    def get_all_comments(self):
        """Получаем корневые комментарии (без родителя)"""
        order_by = self.request.GET.get('order_by', '-date')
        root_comments = Comment.objects.filter(parent__isnull=True).order_by(order_by)
        return root_comments.order_by(order_by)
