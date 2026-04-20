from django.contrib import admin
from .models import Pieteikums, Statuss, Workflow, PieteikumaTips

admin.site.register(Pieteikums)
admin.site.register(Statuss)
admin.site.register(Workflow)
admin.site.register(PieteikumaTips)