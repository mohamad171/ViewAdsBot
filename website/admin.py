from django.contrib import admin
from .models import *


@admin.register(StartedUser)
class StartedUsersAdmin(admin.ModelAdmin):
    list_display = ["id","chat_id","full_name","username"]
    list_filter = ["username","chat_id"]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["id","user","phone","cli_info","proxy_info","is_logged_in","is_active"]


@admin.register(SampleBio)
class SampleBioAdmin(admin.ModelAdmin):
    list_display = ["id","text"]


@admin.register(SampleProfileImage)
class SampleProfileImageAdmin(admin.ModelAdmin):
    list_display = ["id","image_profile"]

@admin.register(CliInfo)
class CliInfoAdmin(admin.ModelAdmin):
    list_display = ["id","api_key","max_account"]

@admin.register(ProxyInfo)
class ProxyInfoAdmin(admin.ModelAdmin):
    list_display = ["id","ip","username","port","max_account"]
    
@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ["id","user","account_count","card_number"]
    
@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ["id","payment_log_channel_id","account_log_channel_id"]
    
