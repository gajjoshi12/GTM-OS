from django.contrib import admin

from .models import Membership, User, Workspace

admin.site.register(User)
admin.site.register(Workspace)
admin.site.register(Membership)
