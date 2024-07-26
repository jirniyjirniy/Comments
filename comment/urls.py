from django.urls import path

from comment.views import CommentView, CommentListView

urlpatterns = [
    path('comment/', CommentView.as_view(), name='comment'),
    path('', CommentListView.as_view(), name='main_page'),
]

