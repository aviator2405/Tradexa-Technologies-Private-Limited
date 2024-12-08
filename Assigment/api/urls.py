from django.urls import path
from .views import CSVUploadAPIView

urlpatterns = [
    # Other routes...
    path('upload-csv/', CSVUploadAPIView.as_view(), name='upload_csv'),
]