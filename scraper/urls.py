from django.urls import path
from .views import ExtractedInfoListView

urlpatterns = [
    path("extracted_info/", ExtractedInfoListView.as_view(), name="extracted_info_list"),
]