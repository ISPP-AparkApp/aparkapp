
from decimal import Decimal

from djmoney.money import Money
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import HttpRequest
from .auxiliary import payment_builder, product_builder, post_reservation_logic
from .models import Announcement, Profile, Reservation, User
from .serializers import (SwaggerBalanceRechargeSerializer,
                          SwaggerProfileBalanceSerializer)


class BalanceStripeAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de saldo de usuario"]

    @swagger_auto_schema(request_body=SwaggerBalanceRechargeSerializer)
    def post(self,request):
        if request.data['amount'] and float(request.data['amount'])>=2.5:
            price_cents=int(Decimal(request.data['amount'])*100)
            try:
                product=product_builder()
                pay_link=payment_builder(price_cents, product['id'],
                "https://aparkapp-s2.herokuapp.com/home/", request.user.id)
                res=Response({"id":pay_link.id, "object":pay_link.object, 
                "active": pay_link.active, "url":pay_link.url}, status.HTTP_200_OK)

            except Exception as e:
                res=Response("La cantidad mínima a depositar es de 5€",status.HTTP_406_NOT_ACCEPTABLE)
        else:
            res=Response("No se ha podido procesar la solicitud",status.HTTP_400_BAD_REQUEST)
        return res

class UserBalanceAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de saldo de usuario"]

    def get(self, request):     ## No se comprueba el usuario para que podáis obtener de cualquiera, si hace falta se cambia
        user=Profile.objects.filter(pk=request.user.id)
        if user:
            res=Response(str(user.get().balance),status.HTTP_200_OK)  
        else:
            res=Response("No existe tal usuario",status.HTTP_404_NOT_FOUND)
        return res
    
    @swagger_auto_schema(request_body=SwaggerProfileBalanceSerializer)
    def put(self, request):
        filter=Profile.objects.filter(pk=request.user.id)
        
        if filter:
            user=filter.get()

            if request.data['funds']:
                funds_amount= round(Decimal(request.data['funds']),2)
                funds_to_money=Money(funds_amount,request.data['funds_currency'])
                if funds_amount< 0:
                    if user.balance >= funds_to_money:
                        user.balance+=funds_to_money
                        user.save()
                        res=Response(status=status.HTTP_204_NO_CONTENT)
                    else:
                        res=Response("No tienes suficiente saldo para realizar la transaccion",status.HTTP_405_METHOD_NOT_ALLOWED)

                elif funds_amount > 0:
                    if funds_amount <5:
                        res=Response("El ingreso mínimo es de 5€",status.HTTP_405_METHOD_NOT_ALLOWED)
                    else:
                        user.balance+=funds_to_money
                        user.save()
                        res=Response(status=status.HTTP_204_NO_CONTENT)
            else:
                res=Response("Petición inválida",status=status.HTTP_400_BAD_REQUEST)
        else:
            res=Response("No puedes añadir saldo a otros usuarios",status=status.HTTP_403_FORBIDDEN) 
        
        return res

class ManageBalanceTransactionsAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de saldo de usuario"]

    @swagger_auto_schema(operation_description="Permite manejo de transacciones (reserva y extensiones) de anuncios introduciendo el id")
    def put(self, request, pk):
        announcement_filter=Announcement.objects.filter(pk=pk)
        session_user=Profile.objects.get(pk=request.user.id)
        if announcement_filter:
            announcement=announcement_filter.get()
            if announcement.user.id == session_user.id:
                reservation=Reservation.objects.get(pk=announcement.id)
                
                petitioner_user=Profile.objects.filter(pk=reservation.user.id)
                extend_announcement_transaction=Money(0.5, 'EUR')
                if petitioner_user.balance > extend_announcement_transaction:
                    petitioner_user.balance-=extend_announcement_transaction
                    petitioner_user.save()

                    session_user.balance+=extend_announcement_transaction  ## Session user is bidding user
                    session_user.save()
                    res=Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    res=Response("No tienes suficiente saldo para realizar la transaccion",status.HTTP_405_METHOD_NOT_ALLOWED)
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
            res=Response("No existe tal anuncio",status.HTTP_404_NOT_FOUND)          
        return res
