from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('active_listings/', views.active_listings, name='active_listings'),  # URL for active listings
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_listing/',views.create_listing, name='create_listing'),
    path('listing/<int:listing_id>/', views.listing_detail, name='listing_detail'),
    path('add_to_watchlist/<int:listing_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('place_bid/<int:listing_id>/', views.place_bid, name='place_bid'),
    path('add_comment/<int:listing_id>/', views.add_comment, name='add_comment'),
    path('remove_from_watchlist/<int:listing_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('watchlist/', views.watchlist, name='watchlist')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
