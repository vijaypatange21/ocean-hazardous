from django.views.generic import ListView
from .models import ExtractedInfo

class ExtractedInfoListView(ListView):
    model = ExtractedInfo
    template_name = "extracted_info_list.html"
    context_object_name = "extracted_infos"
    paginate_by = 10  # Optional: show 10 per page
    ordering = ['-created_at']  # Most recent first