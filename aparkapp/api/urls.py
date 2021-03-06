from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .payments import BalanceStripeAPI, UserBalanceAPI, ManageBalanceTransactionsAPI
from .views import (AnnouncementAPI, AnnouncementsAPI, AnnouncementStatusAPI,
                    AnnouncementsUserAPI, CancelAnnouncementsAPI, CancelReservationAPI, GeolocationToAddressAPI,
                    GeolocationToCoordinatesAPI, Login, ProfileApi, ReservationAPI,
                    ReservationByAnouncementAPI, ReservationsAPI, UsersAPI,
                    UsersVehiclesAPI, VehiclesAPI, VehiclesIdAPI,
                    myAnnouncementsAPI, RegisterAPI, UserAPI, RatingAPI, CreateRatingAPI, myRatingsAPI)
from api.auxiliary import stripe_webhook_view

urlpatterns = [
    path('register/', RegisterAPI.as_view()),
    path('login/', Login.as_view()),
    path('refresh-token/', jwt_views.TokenRefreshView.as_view()),
    path('vehicles/', VehiclesAPI.as_view()),
    path('vehicles/<int:pk>/', VehiclesIdAPI.as_view()),
    path('profiles/', ProfileApi.as_view()),
    path('users/', UsersAPI.as_view()),
    path('users/<int:pk>/', UserAPI.as_view()),
    path('users/vehicles/', UsersVehiclesAPI.as_view()),
    path('announcements/', AnnouncementsAPI.as_view()),
    path('myAnnouncements/', myAnnouncementsAPI.as_view()),
    path('announcements/status/<int:pk>/', AnnouncementStatusAPI.as_view()),
    path('announcement/<int:pk>/', AnnouncementAPI.as_view()),
    path('announcement/user/', AnnouncementsUserAPI.as_view()),
    path('cancel/announcement/<int:pk>/', CancelAnnouncementsAPI.as_view()),
    path('reservation/<int:pk>/', ReservationAPI.as_view()),
    path('reservation/anouncement/<int:pk>/', ReservationByAnouncementAPI.as_view()),
    path('reservations/', ReservationsAPI.as_view()),
    path('reservation/<int:pk>/', ReservationAPI.as_view()),
    path('cancel/reservation/<int:pk>/', CancelReservationAPI.as_view()),
    path('geolocatorToAddress/', GeolocationToAddressAPI.as_view()),
    path('geolocatorToCoordinates/', GeolocationToCoordinatesAPI.as_view()),
    path('userBalanceRecharge/', BalanceStripeAPI.as_view()),
    path('userAccountBalance/', UserBalanceAPI.as_view()),
    path('balanceTransactions/<int:pk>/', ManageBalanceTransactionsAPI.as_view()),
    path('rating/<int:pk>/', RatingAPI.as_view()),
    path('rating/<object>/<int:pk>/', CreateRatingAPI.as_view()),
    path('myRatings/', myRatingsAPI.as_view()),
    path('stripeWebhook/', stripe_webhook_view)
]
