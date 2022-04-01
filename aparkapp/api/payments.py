import os

import stripe
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Announcement, Reservation

load_dotenv() 
API_KEY = os.environ['STRIPE_SECRET']
PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']

stripe.api_key=API_KEY

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
                    pay_link=payment_builder(price_cents, product['id'],"https://aparkapp-s2.herokuapp.com/login")
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
                    reservation_to_extend=Reservation.objects.filter(announcement=pk).get()
                    if reservation_to_extend:
                        if reservation_to_extend.n_extend <3:
                            reservation_to_extend.update(n_extend=reservation_to_extend.n_extend+1)
                            product=product_builder(announcement_to_buy, reservation_to_extend)
                            pay_link=payment_builder(50, product['id'],"https://aparkapp-s2.herokuapp.com/login") ## TODO: change redirect

                            res=Response({"id":pay_link.id, "object":pay_link.object, 
                            "active": pay_link.active, "url":pay_link.url}, status.HTTP_200_OK)
                        else:
                            res=Response("Una reserva no puede ser ampliada más de 3 veces",status.HTTP_400_BAD_REQUEST) 
                    else:
                       res=Response("No se ha encontrado ninguna reserva para el anuncio especificado",status.HTTP_400_BAD_REQUEST) 
                except Exception as e:
                    res=Response("No se ha podido procesar la solicitud",status.HTTP_406_NOT_ACCEPTABLE)
        else:
            res=Response("No se ha encontrado tal anuncio",status.HTTP_404_NOT_FOUND)
        return res    

## Auxiliary methods
def product_builder(announcement):
    return stripe.Product.create(name="Plaza en "+ announcement.location+"\n("+str(announcement.longitude)
        +" , "+str(announcement.latitude)+")")

def product_builder(announcement, reservation):
    return stripe.Product.create(name="Extensión de tiempo de espera nº " + str(reservation.n_extend+1)
        + " en "+ announcement.location+"\n("+str(announcement.longitude)
        +" , "+str(announcement.latitude)+")")


def payment_builder(price, productId, url):
    price=stripe.Price.create(
        unit_amount=price,
        currency="eur",
        product=id,
    )                            
    return stripe.PaymentLink.create(
        line_items=[{"price": price['id'], "quantity": 1}],
            after_completion={
            "type": "redirect",
            "redirect": {"url": url}, 
        })
