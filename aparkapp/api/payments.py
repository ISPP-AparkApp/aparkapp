
from decimal import Decimal

from djmoney.money import Money
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import HttpRequest
from .auxiliary import payment_builder, product_builder, post_reservation_logic, put_announcement_status_logic
from .models import Announcement, Profile, Reservation, User
from .serializers import (SwaggerBalanceRechargeSerializer,
                          SwaggerProfileBalanceSerializer)
from django.shortcuts import get_object_or_404

class BalanceStripeAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de perfiles y saldo de usuario"]

    @swagger_auto_schema(request_body=SwaggerBalanceRechargeSerializer)
    def post(self,request):
        amount=request.data.get('amount')
        if amount:
            if float(amount)>=2.5:
                price_cents=int(Decimal(amount)*100)
                try:
                    product=product_builder()
                    pay_link=payment_builder(price_cents, product['id'],
                    "https://aparkapp-s2.herokuapp.com/home/", request.user.id)
                    res=Response({"id":pay_link.id, "object":pay_link.object, 
                    "active": pay_link.active, "url":pay_link.url}, status.HTTP_200_OK)
                except Exception as e:
                    res=Response("Error en el servicio, inténtelo de nuevo más tarde",status.HTTP_503_SERVICE_UNAVAILABLE)
            else:
               res=Response("La cantidad mínima a depositar es de 2.5€",status.HTTP_406_NOT_ACCEPTABLE) 
        else:
            res=Response("La solicitud no es válida, asegurese de que están todos los campos correctamente",status.HTTP_400_BAD_REQUEST)
        return res

class UserBalanceAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de perfiles y saldo de usuario"]

    def get(self, request):  
        user=Profile.objects.get(pk=request.user.id)
        return Response(str(user.balance),status.HTTP_200_OK)  
    
    @swagger_auto_schema(request_body=SwaggerProfileBalanceSerializer)  ## Allow users to retrieve account balance 
    def put(self, request):
        user=Profile.objects.get(pk=request.user.id)
        if request.data.get('funds'):
            funds_amount= round(Decimal(request.data['funds']),2)
            funds_to_money=Money(funds_amount,request.data['funds_currency'])
            if funds_amount< 0:
                if (user.balance+funds_to_money) >= Money(0.0, user.balance.currency):
                    user.balance+=funds_to_money
                    user.save()
                    res=Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    res=Response("No tienes suficiente saldo para realizar la transaccion",status.HTTP_405_METHOD_NOT_ALLOWED)
            else:
                res=Response("Para retirar fondos introduce una cifra negativo",status.HTTP_406_NOT_ACCEPTABLE)
        else:
            res=Response("Petición inválida",status=status.HTTP_400_BAD_REQUEST)
        
        return res

class ManageBalanceTransactionsAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de perfiles y saldo de usuario"]

    @swagger_auto_schema(operation_description="Permite manejo de transacciones (reservar y extensiones) de anuncios de forma automática introduciendo el id \
    del anuncio sobre el cual operar")
    def put(self, request, pk):
        announcement_filter=Announcement.objects.filter(pk=pk)
        session_user=Profile.objects.get(pk=request.user.id)
        if announcement_filter:
            announcement=announcement_filter.get()
            if announcement.user.id == session_user.id:
                reservation=get_object_or_404(Reservation,announcement=announcement.id)
                petitioner_user=get_object_or_404(Profile,pk=reservation.user.id)
                extend_announcement_transaction=Money(0.5, 'EUR')
                if petitioner_user.balance > extend_announcement_transaction:
                    request=HttpRequest()
                    request.user=petitioner_user
                    request.data={'status': 'AcceptDelay'};
                    res=put_announcement_status_logic(request, announcement.id)
                    if res.status_code == status.HTTP_204_NO_CONTENT:
                        petitioner_user.balance-=extend_announcement_transaction
                        petitioner_user.save()

                        session_user.balance+=extend_announcement_transaction  ## Session user is bidding user
                        session_user.save()
                else:
                    res=Response("No tienes suficiente saldo para realizar la extensión",status.HTTP_409_CONFLICT)
            else:
                reservation_buy_transaction=Money(announcement.price, 'EUR')
                if session_user.balance > reservation_buy_transaction:   ## Session user is petitioner user
                    session_user.balance-=reservation_buy_transaction
                    session_user.save()

                    bidding_user=Profile.objects.get(pk=announcement.user.id)
                    bidding_user.balance+=reservation_buy_transaction
                    bidding_user.save()

                    ## Create reservation
                    req=HttpRequest()
                    req.user=User.objects.get(pk=request.user.id)
                    req.data={'announcement':announcement.id}
                    res=post_reservation_logic(req)
                else:
                    res=Response("No tienes suficiente saldo para realizar la reserva",status.HTTP_409_CONFLICT)
        else:
            res=Response("No existe tal anuncio",status.HTTP_404_NOT_FOUND)          
        return res
