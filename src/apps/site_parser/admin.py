from django.contrib import admin

from .models import Vacancy, City, Company


class AdminVacancy(admin.ModelAdmin):
    list_display = ('title', 'starts_at', 'location', 'company')
    search_fields = ('title', 'company__name')


admin.site.register(City)
admin.site.register(Company)
admin.site.register(Vacancy, AdminVacancy)
