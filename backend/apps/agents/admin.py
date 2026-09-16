from django.contrib import admin

from .models import ActivityEvent, Agent, AgentRun, Command, Decision

admin.site.register([Agent, AgentRun, Decision, Command, ActivityEvent])
