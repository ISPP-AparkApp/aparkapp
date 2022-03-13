from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.contrib.auth.models import User



class User(User):
    phone = models.CharField(max_length=12)
    birthdate = models.DateField()

class Rating(models.Model):
    RATING = ((1, 'Muy mala'), (2,'Mala'), (3,'Regular'), (4,'Buena'), (5,'Muy Buena'))
    id = models.AutoField(primary_key=True)
    rate = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], choices=RATING)
    comment = models.CharField(max_length=500)
    
    #Relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.id


class Vehicle(models.Model):

    SEGA = 'Segmento A'
    SEGB = 'Segmento B'
    SEGC = 'Segmento C'
    SEGD = 'Segmento D'
    SEGE = 'Segmento E'
    SEGF = 'Segmento F'

    TYPE = [
       (SEGA, ('El vehículo pertenece al segmento A')),
       (SEGB, ('El vehículo pertenece al segmento B')),
       (SEGC, ('El vehículo pertenece al segmento C')),
       (SEGD, ('El vehículo pertenece al segmento D')),
       (SEGE, ('El vehículo pertenece al segmento E')),
    ] 
    id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=200)
    model = models.CharField(max_length=400)
    license_plate = models.CharField(max_length=10)
    color = models.CharField(max_length=100)
    type = models.CharField(
       max_length=256,
       choices=TYPE,
       default=SEGA,
    )
    #Relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.id

class Announcement(models.Model):

    PUBLIC = 'Zona libre'
    BLUE = 'Zona Azul'
    GREEN = 'Zona Verde'
    RED = 'Zona Roja'
    ORANGE = 'Zona Naranja'
    MAR = 'Zona MAR'

    TYPE = [
       (PUBLIC, ('La plaza está situada en una zona libre')),
       (BLUE, ('La plaza está situada en zona azul')),
       (GREEN, ('La plaza está situada en zona verde')),
       (RED, ('La plaza está situada en zona roja')),
       (ORANGE, ('La plaza está situada en zona naranja')),
       (MAR, ('La plaza está situada en zona de muy alta rotación'))
    ] 

    INITIAL = 'Initial'
    ARRIVAL = 'Arrival'
    DEPARTURE = 'Departure'

    STATUS = [
       (INITIAL, ('Estado inicial')),
       (ARRIVAL, ('Estado llegada')),
       (DEPARTURE, ('Estado salida')),
    ] 

    id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    wait_time = models.IntegerField()
    price = models.FloatField(validators=[MinValueValidator(0.5), MaxValueValidator(10)])
    allow_wait = models.BooleanField(default=False)
    location = models.CharField(max_length=1024)
    zone = models.CharField(
       max_length=256,
       choices=TYPE,
       default=PUBLIC,
    )
    limited_mobility = models.BooleanField(default=False)
    status = models.CharField(
       max_length=256,
       choices=STATUS,
       default=INITIAL,
    )
    observation = models.CharField(max_length=500)
    rated = models.BooleanField(default=False)

    #Relationship
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.id

class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    n_extend = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)])
    cancelled = models.BooleanField(default=False)
    rated = models.BooleanField(default=False)


    #Relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    announcement = models.OneToOneField(Announcement, on_delete=models.CASCADE)


    def __str__(self):
        return self.id
