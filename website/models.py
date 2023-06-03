from django.db import models


class StartedUser(models.Model):
    chat_id = models.CharField(max_length=20)
    full_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,null=True,blank=True)
    credit = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Account(models.Model):
    user = models.ForeignKey(StartedUser,on_delete=models.SET_NULL,null=True,related_name="accounts")
    phone = models.CharField(max_length=15)
    session_string = models.TextField(null=True)
    is_logged_in = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    bio = models.TextField(null=True,blank=True)
    image_profile = models.ImageField(upload_to="account/profiles",null=True)
    session_file = models.FileField(upload_to="sessions",null=True)

    def __str__(self):
        return self.phone


class SampleBio(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text


class SampleProfileImage(models.Model):
    image_profile = models.ImageField(upload_to="sample/profiles")

    def __str__(self):
        return self.image_profile.name