from django.db import models
from django.contrib.auth import get_user_model
import uuid
User = get_user_model()

# Create your models here.

class Profile(models.Model):
    firstname = models.CharField(max_length= 64, blank= True)
    lastname = models.CharField(max_length= 64, blank= True)
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(max_length= 25, blank=True)
    profileimg = models.ImageField(upload_to= 'profile_image', default='blank-profile-picture.png')
    location = models.CharField(max_length= 100, blank= True)

    def get_username(self):
        return self.user.username
    
    def get_short_bio(self):
        return self.bio[:10] + ' ...'

    def __str__(self):
        # we can have access to user model fields from foreign key
        return self.user.username


class Post(models.Model):
    # primary key = True → means that set uuid for default id
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    # what cascade does
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    owner_profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    no_of_likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='post')  
    caption = models.TextField()

    def add_likes(self):
        self.no_of_likes += 1
        self.save()
    
    def sub_likes(self):
        self.no_of_likes -= 1
        self.save()

class Like(models.Model):
    post_id = models.CharField(max_length=50)
    user = models.CharField(max_length= 100)

class Follower(models.Model):
    user = models.CharField(max_length=100)
    follower = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.follower} Follows {self.user}'