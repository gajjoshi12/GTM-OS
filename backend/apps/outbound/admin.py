from django.contrib import admin

from .models import Enrollment, OutboundMessage, Reply, Sequence

admin.site.register([Sequence, Enrollment, OutboundMessage, Reply])
