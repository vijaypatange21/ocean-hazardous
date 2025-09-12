from django.contrib import admin
from .models import Report, ReportComment

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'status', 'created_by', 'submitted_to', 'created_at']
    list_filter = ['status', 'report_type', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'submitted_at']

@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ['report', 'user', 'created_at']
    list_filter = ['created_at']
