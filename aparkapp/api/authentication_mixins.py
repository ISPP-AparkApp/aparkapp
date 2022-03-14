from rest_framework.response import Response
from .authentication import ExpiringTokenAuthentication
from rest_framework.authentication import get_authorization_header
from rest_framework.renderers import JSONRenderer
from rest_framework import status

class Authentication(object):
    user = None
    user_token_expired = False

    def get_users(self,request):
        token = get_authorization_header(request).split()
        if token:
            try:
                token = token[1].decode()
            except:
                return None
            token_expire = ExpiringTokenAuthentication()
            user,token,message,self.user_token_expired = token_expire.authenticate_credentials(token)
            if user != None and token != None:
                self.user = user
                return user
            return message
        return None

    def dispatch(self,request):
        user = self.get_users(request)
        if user is not None:
            if type(user) == str:
                response = Response({'error':user,'expired':self.user_token_expired}, status= status.HTTP_400_BAD_REQUEST)
                response.accepted_renderer = JSONRenderer()
                response.accepted_media_type = 'applicaction/json'
                response.renderer_context = {}
                return response
            
            if not self.user_token_expired:
                return  super().dispatch(request)
        response = Response({'error':'Token not sent','expired':self.user_token_expired},status= status.HTTP_400_BAD_REQUEST)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = 'applicaction/json'
        response.renderer_context = {}
        return response