from django.contrib import admin
from trainer.models import DomainPrefix,SquatedWord,Brand,  TopLevelDomain,KeyWord, Model


# Register your models here.

admin.site.register(DomainPrefix)
admin.site.register(Brand)
admin.site.register(SquatedWord)
admin.site.register(TopLevelDomain)
admin.site.register(KeyWord)
admin.site.register(Model)

