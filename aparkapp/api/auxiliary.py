import datetime

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from djmoney.money import Money

from .models import Announcement, Reservation, Profile

## File for auxiliary methods to improve general readibility of the project

### PAYMENTS AUXILIARY
@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
        payload, signature_header, settings.ENDPOINT_SECRET
    )   
        res=HttpResponse(status=200) 
    except ValueError as e:
        # Invalid payload
        res= HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        res=HttpResponse(status=400)

    # Handle operations after payment succeeded event
    if (event['type'] == 'checkout.session.completed'):
        session = event['data']['object']
        session['cancel_url']='https://aparkapp-s2.herokuapp.com/home'
        # Fulfill the purchase
        post_order_operations(session, session['metadata'])
    elif event['type'] == 'checkout.session.expired' or event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']
        session['cancel_url']='https://aparkapp-s2.herokuapp.com/home'
    # Passed signature verification
    return res

    
def post_order_operations(session, metadata):
    stripe.PaymentLink.modify(
        session['payment_link'],
        active=False,
    )
    user=Profile.objects.get(pk=metadata['user_id'])
    user.balance+=Money(session['amount_total']/100, session['currency'])
    user.save()
    return HttpResponse(status=201)

## PAYMENT LINK BUILDERS

def product_builder():
    return stripe.Product.create(name="Recarga de saldo AparkApp")

def payment_builder(price, productId, url, user_id):
    price=stripe.Price.create(
        unit_amount=price,
        currency="eur",
        product=productId,
    )                   
    return stripe.PaymentLink.create(line_items=[{"price": price['id'], "quantity": 1}], 
            after_completion={"type": "redirect", "redirect": {"url": url}},
            metadata={'user_id': user_id})

### RESERVATION LOGIC

def post_reservation_logic(request):
    announcement_to_book=get_object_or_404(Announcement,pk=request.data['announcement'])
    temp_date=make_aware(datetime.datetime.now())
    if Reservation.objects.filter(announcement=announcement_to_book):
        response= Response("El anuncio ya está reservado.",status=status.HTTP_409_CONFLICT)
    elif announcement_to_book.user == request.user:
        response= Response("No puedes reservar tu propio anuncio.",status=status.HTTP_405_METHOD_NOT_ALLOWED)
    else: 
        Reservation.objects.create(date=datetime.datetime(temp_date.year, temp_date.month, temp_date.day, temp_date.hour, temp_date.minute), 
        cancelled=False, rated=False, user=request.user, announcement=announcement_to_book)
        response=Response("La reserva ha sido creada",status=status.HTTP_201_CREATED)
    return response

### ANNOUNCEMENT LOGIC 

def put_announcement_status_logic(request, pk):
    try:
        request_status= request.data.get("status")
        if request_status:
            announcement_to_update=Announcement.objects.get(pk=pk)
            if announcement_to_update:
                if request_status=="AcceptDelay":
                    if announcement_to_update.n_extend>=3:
                        res=Response("error: n_extend es mayor o igual a 3",status=status.HTTP_400_BAD_REQUEST)
                    else:
                        announcement_to_update.status = request_status
                        announcement_to_update.wait_time += 5
                        announcement_to_update.n_extend += 1
                        announcement_to_update.save()
                        res=Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    announcement_to_update.status = request_status
                    announcement_to_update.save()
                    res=Response(status=status.HTTP_204_NO_CONTENT)
        else:
            res=Response("La petición es inválida", status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        res=Response("No existe el anuncio especificado", status=status.HTTP_404_NOT_FOUND)
    
    return res
