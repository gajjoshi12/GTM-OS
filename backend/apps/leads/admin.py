from django.contrib import admin

from .models import ICP, Company, Contact

admin.site.register([ICP, Company, Contact])
