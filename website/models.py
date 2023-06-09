from django.db import models
from django.db.models.signals import post_save, pre_delete,pre_save,post_delete
from django.dispatch import receiver

class StartedUser(models.Model):
    chat_id = models.CharField(max_length=20)
    full_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,null=True,blank=True)
    credit = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class CliInfo(models.Model):
    api_key = models.CharField(max_length=32)
    api_hash = models.CharField(max_length=64)
    max_account = models.IntegerField(default=1)
    can_use = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)



    def __str__(self):
        return self.api_key


class ProxyInfo(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    ip = models.CharField(max_length=20)
    port = models.IntegerField()
    max_account = models.IntegerField(default=1)
    can_use = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.ip


class Account(models.Model):
    user = models.ForeignKey(StartedUser,on_delete=models.SET_NULL,null=True,blank=True,related_name="accounts")
    cli_info = models.ForeignKey(CliInfo,on_delete=models.SET_NULL,null=True,blank=True,related_name="cli_accounts")
    proxy_info = models.ForeignKey(ProxyInfo,on_delete=models.SET_NULL,null=True,related_name="proxy_accounts")
    phone = models.CharField(max_length=15)
    session_string = models.TextField(null=True)
    is_logged_in = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_checkout = models.BooleanField(default=False)
    bio = models.TextField(null=True,blank=True)
    image_profile = models.ImageField(upload_to="account/profiles",null=True,blank=True)
    session_file = models.FileField(upload_to="sessions",null=True)
    device_model = models.CharField(max_length=15,null=True,blank=True)
    system_version = models.CharField(max_length=20,null=True,blank=True)
    app_version = models.CharField(max_length=10,null=True,blank=True)
    last_used = models.DateTimeField(null=True,blank=True)


    def __str__(self):
        return self.phone


class Checkout(models.Model):
    user = models.ForeignKey(StartedUser,on_delete=models.SET_NULL,null=True,related_name="checkouts")
    account_count = models.IntegerField()
    card_number = models.CharField(max_length=16)
    

    def __str__(self):
        return self.card_number


class SampleBio(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text


class SampleProfileImage(models.Model):
    image_profile = models.ImageField(upload_to="sample/profiles")

    def __str__(self):
        return self.image_profile.name


class Order(models.Model):
    class OrderTypeChoices(models.IntegerChoices):
        VIEW = 0,"View"
        JOIN = 1,"Join"
    
    class OrderStatusChoices(models.IntegerChoices):
        WATING = 0,"Wating"
        RUNNING = 1,"Running"
        FINISHED = 2,"Finished"

    order_type = models.IntegerField(choices=OrderTypeChoices.choices)
    count = models.IntegerField()
    user = models.ForeignKey(StartedUser,on_delete=models.SET_NULL,null=True)
    start_at = models.DateTimeField()
    accept_to_start = models.BooleanField(default=False)
    link = models.TextField()
    status = models.IntegerField(choices=OrderStatusChoices.choices)
    success_count = models.IntegerField(default=0)
    faild_count = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.get_order_type_display()

    
@receiver(post_save, sender=Account)
def create_account(sender, instance, created, **kwargs):
    if created:
        cli_info = instance.cli_info
        if cli_info.cli_accounts.filter().count() >= cli_info.max_account:
            cli_info.can_use = False
            cli_info.save()

        proxy_info = instance.proxy_info
        if proxy_info.proxy_accounts.filter().count() >= proxy_info.max_account:
            proxy_info.can_use = False
            proxy_info.save()

        # change_bio_details(instance.phone,instance.bio,instance.image_profile.path)
        
@receiver(post_delete, sender=Account)
def post_delete_account(sender, instance, *args, **kwargs):
    try:
        instance.session_file.delete(save=False)
    except:
        pass


