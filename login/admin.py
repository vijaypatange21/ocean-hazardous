from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, HazardReport, HazardMedia, HazardHotspot, ReportFeedback

# Inline admin for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('user_type', 'phone_number', 'department')

# Extend the existing UserAdmin
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_user_type', 'is_active', 'date_joined')
    list_filter = ('is_active', 'date_joined', 'userprofile__user_type')
    
    def get_user_type(self, obj):
        try:
            return obj.userprofile.user_type
        except UserProfile.DoesNotExist:
            return 'No Profile'
    get_user_type.short_description = 'User Type'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register UserProfile separately for direct management
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone_number', 'department', 'created_at']
    list_filter = ['user_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number', 'department']
    readonly_fields = ['created_at']

# Register HazardReport with enhanced admin interface
@admin.register(HazardReport)
class HazardReportAdmin(admin.ModelAdmin):
    list_display = [
        'report_id', 'reporter', 'hazard_type', 'severity', 
        'status', 'urgent', 'location_name', 'created_at'
    ]
    list_filter = [
        'hazard_type', 'severity', 'status', 'urgent', 
        'created_at', 'verified_at'
    ]
    search_fields = [
        'report_id', 'description', 'location_name', 
        'reporter__username', 'reporter__first_name', 'reporter__last_name'
    ]
    readonly_fields = ['report_id', 'created_at', 'updated_at', 'verified_at']
    
    # Organize fields in fieldsets for better admin interface
    fieldsets = (
        ('Report Information', {
            'fields': ('report_id', 'reporter', 'hazard_type', 'severity', 'urgent')
        }),
        ('Location Details', {
            'fields': ('latitude', 'longitude', 'location_name')
        }),
        ('Description & Contact', {
            'fields': ('description', 'contact_number')
        }),
        ('Status & Verification', {
            'fields': ('status', 'verified_by', 'admin_notes'),
            'classes': ('collapse',)  # Collapsible section
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'verified_at'),
            'classes': ('collapse',)
        })
    )
    
    # Add actions for bulk operations
    actions = ['mark_as_verified', 'mark_as_pending', 'mark_as_investigating']
    
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(status='verified', verified_by=request.user)
        self.message_user(request, f'{updated} reports marked as verified.')
    mark_as_verified.short_description = "Mark selected reports as verified"
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} reports marked as pending.')
    mark_as_pending.short_description = "Mark selected reports as pending"
    
    def mark_as_investigating(self, request, queryset):
        updated = queryset.update(status='investigating')
        self.message_user(request, f'{updated} reports marked as under investigation.')
    mark_as_investigating.short_description = "Mark selected reports as investigating"

# Register HazardMedia
@admin.register(HazardMedia)
class HazardMediaAdmin(admin.ModelAdmin):
    list_display = ['report', 'media_type', 'file_name', 'file_size_display', 'uploaded_at']
    list_filter = ['media_type', 'uploaded_at']
    search_fields = ['report__report_id', 'description']
    readonly_fields = ['file_size', 'uploaded_at']
    
    def file_name(self, obj):
        return obj.file.name.split('/')[-1] if obj.file else 'No file'
    file_name.short_description = 'File Name'
    
    def file_size_display(self, obj):
        return obj.get_file_size_display() if obj.file_size else 'Unknown'
    file_size_display.short_description = 'File Size'

# Register HazardHotspot
@admin.register(HazardHotspot)
class HazardHotspotAdmin(admin.ModelAdmin):
    list_display = ['name', 'latitude', 'longitude', 'report_count', 'is_active', 'last_updated']
    list_filter = ['is_active', 'last_updated']
    search_fields = ['name']
    readonly_fields = ['last_updated']
    
    fieldsets = (
        ('Location Information', {
            'fields': ('name', 'latitude', 'longitude', 'radius')
        }),
        ('Statistics', {
            'fields': ('report_count', 'is_active', 'last_updated')
        })
    )

# Register ReportFeedback
@admin.register(ReportFeedback)
class ReportFeedbackAdmin(admin.ModelAdmin):
    list_display = ['report', 'user', 'feedback_type', 'created_at']
    list_filter = ['feedback_type', 'created_at']
    search_fields = ['report__report_id', 'user__username', 'comment']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Feedback Details', {
            'fields': ('report', 'user', 'feedback_type')
        }),
        ('Comment', {
            'fields': ('comment',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )

# Customize admin site header and title
admin.site.site_header = "Ocean Hazard System Administration"
admin.site.site_title = "Ocean Hazard Admin"
admin.site.index_title = "Welcome to Ocean Hazard System Admin Portal"