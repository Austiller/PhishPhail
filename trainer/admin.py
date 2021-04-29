from django.contrib import admin
from trainer.models import FQDN,DomainPrefix,SquatedWord,Brand, Tag, TopLevelDomain,KeyWord, Model


# Register your models here.
admin.site.register(FQDN)
admin.site.register(DomainPrefix)
admin.site.register(Brand)
admin.site.register(SquatedWord)
admin.site.register(TopLevelDomain)
admin.site.register(KeyWord)
admin.site.register(Tag)
admin.site.register(Model)

