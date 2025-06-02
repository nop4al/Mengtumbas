from django.urls import path
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('password_change/', PasswordChangeView.as_view(template_name='accounts/password_change.html', success_url='/accounts/password_change/done/'), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('orders/', views.order_history, name='order_history'),
    path('review/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('review/add/<int:order_item_id>/', views.add_review, name='add_review'),
]
