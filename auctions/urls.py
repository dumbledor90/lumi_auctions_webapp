from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("profile/<str:username>/", views.IndexView.as_view(), name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create/', views.create_listing, name='create-listing'),
    path('detail/<int:pk>/', views.listing_detail, name='listing-detail'),
    path('update/<int:pk>/', views.ListingUpdateView.as_view(), name='update-listing'),
    path('delete/<int:pk>/', views.ListingDeleteView.as_view(), name='delete-listing'),
    path('close/<int:pk>/', views.close_listing, name='close-listing'),
    path('watchlist/', views.WatchlistView.as_view(), name='watchlist'),
    path('c/', views.category_view, name='categories'),
    path('c/<str:category_name>', views.category_view, name='categories'),
]
