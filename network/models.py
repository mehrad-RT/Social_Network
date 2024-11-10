from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    content =models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name="author")
    date = models.DateTimeField(auto_now_add=True)
    liked = models.ManyToManyField('User', default=None, blank=True, related_name='post_likes')

    def __str__(self):
        return f"post {self.id} written by {self.user} on {self.date.strftime('%d %b %Y %H:%M:%S')}"
    
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name="followingUser")
    user_follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name= "followedUser")

    def __str__(self):
        return f"{self.user} is following {self.user_follower}"
    
class Like(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='post_like')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_likes',null=True)
     
    def __str__(self):
       return f"{self.user}-Liked-{self.post}"