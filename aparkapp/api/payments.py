import os

import stripe
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Announcement

load_dotenv() 
API_KEY = os.environ['STRIPE_SECRET']
PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']

stripe.api_key=API_KEY

class StripePaymentsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request, pk):
        announcement_to_buy=Announcement.objects.get(pk=pk)
        price_cents=int(announcement_to_buy.price*100)
        if announcement_to_buy.user == request.user:
             res=Response("No puedes comprar tu propio anuncio", status=status.HTTP_403_FORBIDDEN)
        else:
            try:
                product=stripe.Product.create(name="Plaza en "+ announcement_to_buy.location+"\n("+
                str(announcement_to_buy.longitude)+","+str(announcement_to_buy.latitude)+")")
                price=stripe.Price.create(
                    unit_amount=price_cents,
                    currency="eur",
                    product=product['id'],
                )
                pay_link=stripe.PaymentLink.create(
                line_items=[{"price": price['id'], "quantity": 1}],
                    after_completion={
                    "type": "redirect",
                    "redirect": {"url": "https://aparkapp-s2.herokuapp.com/login"},
                },
                )
                print(pay_link)
                res=Response(pay_link,status.HTTP_200_OK)
            except Exception as e:
                res=Response("No se ha podido procesar la solicitud",status.HTTP_406_NOT_ACCEPTABLE)
        return res

