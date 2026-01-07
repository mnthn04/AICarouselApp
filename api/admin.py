from django.contrib import admin

# Register your models here.
from .models import CarouselProject, Slide, CarouselTemplate
admin.site.register(CarouselProject)
admin.site.register(Slide)
admin.site.register(CarouselTemplate)