from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from simple_history.admin import SimpleHistoryAdmin

from exchange_core.admin import BaseAdmin
from binary.models import BinaryTree, Report


@admin.register(BinaryTree)
class BinaryTreeAdmin(BaseAdmin):
    list_display = ['user', 'id', 'parent', 'position', 'value']
    search_fields = ['user__first_name', 'user__email', 'user__document_1', 'user__document_2']
    ordering = ('-created',)
    readonly_fields = ['user', 'id', 'parent', 'position', 'value']

    def has_add_permission(self, request, o=None):
        return False

    def has_edit_permission(self, request, o=None):
        return False


@admin.register(Report)
class BinaryTreeAdmin(BaseAdmin):
    list_display = ['left_value', 'right_value', 'lower_side']
    search_fields = ['statement__account__user__first_name', 'statement__account__user__email', 'statement__account__user__document_1', 'statement__account__user__document_2']
    ordering = ('-created',)
    readonly_fields = ['left_value', 'right_value', 'lower_side']

    def has_add_permission(self, request, o=None):
        return False

    def has_edit_permission(self, request, o=None):
        return False

