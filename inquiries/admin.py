"""
Django admin configuration for Inquiry and LeadStatusHistory.
"""
from django.contrib import admin
from inquiries.models import Inquiry, LeadStatusHistory, FollowUpNote


class FollowUpNoteInline(admin.TabularInline):
    model = FollowUpNote
    extra = 0
    can_delete = False
    readonly_fields = ('content', 'created_by', 'created_at')


class LeadStatusHistoryInline(admin.TabularInline):
    model = LeadStatusHistory
    extra = 0
    can_delete = False
    readonly_fields = ('previous_status', 'new_status', 'updated_by', 'remarks', 'created_at')


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = (
        'reference_id',
        'full_name',
        'mobile_number',
        'email',
        'service',
        'status',
        'created_at',
    )
    list_filter = ('status', 'service', 'created_at')
    search_fields = ('reference_id', 'full_name', 'mobile_number', 'email')
    readonly_fields = ('reference_id', 'created_at', 'updated_at')
    inlines = [FollowUpNoteInline, LeadStatusHistoryInline]
    ordering = ('-created_at',)


@admin.register(FollowUpNote)
class FollowUpNoteAdmin(admin.ModelAdmin):
    list_display = ('inquiry', 'created_by', 'created_at')
    search_fields = ('inquiry__reference_id', 'inquiry__full_name', 'content')
    readonly_fields = ('inquiry', 'created_by', 'created_at')
    ordering = ('-created_at',)


@admin.register(LeadStatusHistory)
class LeadStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('inquiry', 'previous_status', 'new_status', 'updated_by', 'created_at')
    list_filter = ('new_status', 'previous_status', 'created_at')
    search_fields = ('inquiry__reference_id', 'inquiry__full_name', 'updated_by__username')
    readonly_fields = ('inquiry', 'previous_status', 'new_status', 'updated_by', 'remarks', 'created_at')
    ordering = ('-created_at',)
