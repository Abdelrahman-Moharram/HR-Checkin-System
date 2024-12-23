from django.db import models
from django.conf import settings



class Location(models.Model):
    latitude    = models.FloatField()
    longitude   = models.FloatField()


    class Meta:
        unique_together = ('latitude', 'longitude',)
    def __str__(self):
        return f'({str(self.longitude)}, {str(self.latitude)})'
    


class Office (models.Model):
    name        = models.CharField(max_length=50)

    @property
    def location(self):
        office_loc = Office_Location.objects.filter(office=self, is_present=True).first()
        if office_loc:
            return office_loc.location
        return None
    
    @property
    def locations(self):
        return Location.objects.filter(location_office_location__office=self, location_office_location__is_present=True)
        

    def __str__(self):
        return self.name
    

class Office_Location(models.Model):
    office     = models.ForeignKey(Office, related_name='office_office_location', on_delete=models.CASCADE)
    location   = models.ForeignKey(Location, related_name='location_office_location', on_delete=models.CASCADE)
    is_present = models.BooleanField(default=True)
    office_sq  = models.FloatField(default=0)
    
    class Meta:
        unique_together = ('office', 'is_present','location')

    def __str__(self):
        return f'Office {self.office} has Location {self.location}'

    

class Attendance(models.Model):
    check_in    = models.DateTimeField(auto_now=False, auto_now_add=True)
    check_out   = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    office      = models.ForeignKey(Office, on_delete=models.CASCADE)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)




