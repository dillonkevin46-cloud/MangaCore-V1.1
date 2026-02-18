from django.contrib import admin
from .models import Ticket, Comment

class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'priority', 'creator', 'assigned_agent', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'description')
    inlines = [CommentInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
