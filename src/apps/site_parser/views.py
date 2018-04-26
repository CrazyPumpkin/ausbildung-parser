from rest_framework import generics

from .serializers import VacancySerializer
from .models import Vacancy


class VacanciesView(generics.ListAPIView):
    """
    Get vacancies list API
    """
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
