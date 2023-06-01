from django.contrib import admin
from .models import *


@admin.register(StartedUser)
class StartedUsersAdmin(admin.ModelAdmin):
    list_display = ["id","chat_id","full_name","username"]
    list_filter = ["username","chat_id"]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["id","user","phone","is_logged_in","is_active"]


@admin.register(SampleBio)
class SampleBioAdmin(admin.ModelAdmin):
    list_display = ["id","text"]


@admin.register(SampleProfileImage)
class SampleProfileImageAdmin(admin.ModelAdmin):
    list_display = ["id","image_profile"]
