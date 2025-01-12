from django.contrib import admin
from diario.models import Diario, Pessoa


class DiarioAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tags', 'create_at']

admin.site.register(Pessoa)
admin.site.register(Diario, DiarioAdmin)
