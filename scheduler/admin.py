from __future__ import unicode_literals

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin, ImportMixin, ExportActionModelAdmin

from .models import BaseUser, Show, Choice

class BaseUserResource(resources.ModelResource):

		class Meta:
			model = BaseUser
			fields = ('id', 'first_name', 'last_name', 'credits',)

class ChoiceResource(resources.ModelResource):

		class Meta:
			model = Choice

class BaseUserAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = BaseUserResource

class ShowAdmin(ImportExportMixin, admin.ModelAdmin):
	
		class Meta:
			model = Show 
			fields = ('id', 'show_name', 'dj', 'co_dj', 'genre', 'tagline', 'day', 'time', 'timestamp')

class ChoiceAdmin(ImportExportMixin, admin.ModelAdmin):
    	
    	class Meta:
    		model = Choice
    		fields = ('id', 'show', 'choice_num', 'day', 'time', 'not_available')

admin.site.register(BaseUser, BaseUserAdmin)
admin.site.register(Show, ShowAdmin)
admin.site.register(Choice, ChoiceAdmin)