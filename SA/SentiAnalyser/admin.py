# Register your models here.
from django.contrib import admin
from .models import RegisteredUser
from .models import AnalyzerData

admin.site.register(RegisteredUser)

admin.site.register(AnalyzerData)