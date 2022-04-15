from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .auxiliary import (extended_product_builder, payment_builder,
                        product_builder)
from .models import Announcement
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from random import randint
from drf_yasg.utils import swagger_auto_schema
from .serializers import SwaggerSeleniumPaymentsSerializer
from platform import system
import time

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

class SeleniumPaymentAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de pagos"]

    @swagger_auto_schema(request_body=SwaggerSeleniumPaymentsSerializer)
    def post(self, request):
        options=webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--start-maximized")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.add_argument('--headless')
        if system() == "Windows":
            path="..\seleniumDrivers\chromedriver-windows.exe"
            options.binary_location= "../browsers/chrome-win/chrome.exe"
        elif system() == "Linux":
            path=".\seleniumDrivers\chromedriver-linux"
            
            options.binary_location="../browsers/chrome-linux/chrome"
        elif system() == "MacOS":
            options.binary_location="../browsers/chrome-mac/Chromium.app/Contents/MacOS/Chromium"
            try:
                path="../seleniumDrivers/chromedriver-mac"
            except Exception:
                path="../seleniumDrivers/chromedriver-mac-m1"

        driver=webdriver.Chrome(executable_path=path,chrome_options=options)
        driver.delete_all_cookies()
        try:
            driver.get(request.data["payment_link"])
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, 
            "//*[@id=\"root\"]/div/div/div[2]/div/div[2]/form/div[2]/div[2]/button/div[3]")))
            email=driver.find_element_by_xpath("//*[@id=\"email\"]")
            email.send_keys(request.user.email)
            credit_card=driver.find_element_by_xpath("//*[@id=\"cardNumber\"]")
            credit_card.send_keys("4242 4242 4242 4242")
            expire_data=driver.find_element_by_xpath("//*[@id=\"cardExpiry\"]")
            expire_data.send_keys(str(randint(1,12))+str(randint(22,70)))
            cvc=driver.find_element_by_xpath("//*[@id=\"cardCvc\"]")
            cvc.send_keys(str(randint(100, 999)))
            owner=driver.find_element_by_xpath("//*[@id=\"billingName\"]")
            owner.send_keys(request.user.first_name + " " +request.user.last_name)
            submit=driver.find_element_by_xpath("//*[@id=\"root\"]/div/div/div[2]/div/div[2]/form/div[2]/div[2]/button/div[3]")
            submit.click()
            time.sleep(3)  ## CHECK TIME 
            res=Response("Petición realizada con éxito",status.HTTP_200_OK)
        except Exception:
            res=Response("Vaya...no se ha podido procesar la solicitud. Inténtelo de nuevo más tarde.",status.HTTP_503_SERVICE_UNAVAILABLE)
        finally:
            driver.quit()
        return Response("Petición realizada con éxito",status.HTTP_200_OK)
