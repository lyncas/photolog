from django.contrib import admin
from .models import InputFile, Image, Project, InputXls


admin.site.register(InputFile)
admin.site.register(Image)
admin.site.register(Project)
admin.site.register(InputXls)
