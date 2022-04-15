
from decimal import Decimal
from djmoney.money import Money
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .auxiliary import (extended_product_builder, payment_builder,
                        product_builder)
from .models import Announcement, Profile
from .serializers import SwaggerProfileBalanceSerializer


class StripePaymentsAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de pagos"]

    def post(self,request, pk):
        announcement_to_buy=Announcement.objects.filter(pk=pk)
        if announcement_to_buy:

            announcement_to_buy=announcement_to_buy.get()

            if announcement_to_buy.user == request.user:
                res=Response("No puedes comprar tu propio anuncio", status=status.HTTP_403_FORBIDDEN)

            else:
                price_cents=int(announcement_to_buy.price*100)
                try:
                    product=product_builder(announcement_to_buy)
                    pay_link=payment_builder(price_cents, product['id'],
                    "https://aparkapp-s2.herokuapp.com/reserve/" + str(announcement_to_buy.id),
                    request.user.id, announcement_to_buy.id)
                    res=Response({"id":pay_link.id, "object":pay_link.object, 
                    "active": pay_link.active, "url":pay_link.url}, status.HTTP_200_OK)

                except Exception as e:
                    res=Response("No se ha podido procesar la solicitud",status.HTTP_406_NOT_ACCEPTABLE)
        else:
            res=Response("No se ha encontrado tal anuncio",status.HTTP_404_NOT_FOUND)
        return res

class StripeExtendedPaymentsAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de pagos"]
    
    def post(self,request, pk):
        announcement_to_buy=Announcement.objects.filter(pk=pk)
        if announcement_to_buy:
            announcement_to_buy=announcement_to_buy.get()
            if announcement_to_buy.user == request.user:
                res=Response("No puedes comprar tu propio anuncio", status=status.HTTP_403_FORBIDDEN)
            else:
                try:
                    if announcement_to_buy.n_extend <3:
                        announcement_to_buy.n_extend+=1
                        announcement_to_buy.save()
                        product=extended_product_builder(announcement_to_buy)
                        pay_link=payment_builder(50, product['id'],
                        "https://aparkapp-s2.herokuapp.com/reserve/" + str(announcement_to_buy.id), 
                        request.user.id, announcement_to_buy.id) 
                        res=Response({"id":pay_link.id, "object":pay_link.object, 
                        "active": pay_link.active, "url":pay_link.url}, status.HTTP_200_OK)
                    else:
                        res=Response("Un anuncio no puede ser ampliado más de 3 veces",status.HTTP_400_BAD_REQUEST) 
                except Exception as e:
                    res=Response("No se ha podido procesar la solicitud",status.HTTP_406_NOT_ACCEPTABLE)
        else:
            res=Response("No se ha encontrado tal anuncio",status.HTTP_404_NOT_FOUND)
        return res    


class UserBalanceAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de saldo de usuario"]

    def get(self, request, pk):     ## No se comprueba el usuario para que podáis obtener de cualquiera, si hace falta se cambia
        user=Profile.objects.filter(pk=pk)
        if user:
            res=Response(str(user.get().balance),status.HTTP_200_OK)  
        else:
            res=Response("No existe tal usuario",status.HTTP_404_NOT_FOUND)
        return res
    
    @swagger_auto_schema(request_body=SwaggerProfileBalanceSerializer)
    def put(self, request, pk):
        filter=Profile.objects.filter(pk=pk)
        
        if filter:
            user=filter.get()
            if request.user.id == user.id:
                if request.data['funds']:
                    funds=request.data['funds']
                    if funds< 0:
                        if user.balance >= funds:
                            user.balance-=Money(round(Decimal(funds),2), request.data['funds_currency'])
                            user.save()
                            res=Response(status=status.HTTP_204_NO_CONTENT)
                        else:
                            res=Response("No tienes suficiente saldo para realizar la transaccion",status.HTTP_409_CONFLICT)

                    elif funds > 0:
                        if funds <5:
                            res=Response("El ingreso mínimo es de 5€",status.HTTP_405_METHOD_NOT_ALLOWED)
                        else:
                            user.balance+=Money(round(Decimal(funds),2), request.data['funds_currency'])
                            user.save()
                            res=Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    res=Response("Petición inválida",status=status.HTTP_400_BAD_REQUEST)
            else:
                res=Response("No puedes añadir saldo a otros usuarios",status=status.HTTP_403_FORBIDDEN) 
        else:
            res=Response("No existe tal usuario",status.HTTP_404_NOT_FOUND)
        
        return res
