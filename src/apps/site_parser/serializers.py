from .models import Vacancy, City, Company
from rest_framework import serializers


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('name', 'logo')


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('name',)


class VacancySerializer(serializers.ModelSerializer):

    company = CompanySerializer()
    location = serializers.SerializerMethodField()
    starts_at = serializers.DateTimeField(format="%d.%m.%Y")

    def get_location(self, obj):
        try:
            return obj.location.name
        except:
            return ""

    class Meta:
        model = Vacancy
        fields = ('is_active', 'title', 'location', 'starts_at',
                  'description', 'image_list', 'company')
