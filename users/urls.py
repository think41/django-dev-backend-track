from django.urls import path

from .views import AdminApproveUserView, AdminUsersListView, LoginView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    # Admin
    path("admin/users/", AdminUsersListView.as_view(), name="admin-users"),
    path("admin/users/<int:pk>/approve/", AdminApproveUserView.as_view(), name="admin-users-approve"),
]

