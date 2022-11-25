from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete

# Create your models here.
class Profile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField("Name",max_length=100,null=True, blank=True)
    surname = models.CharField("Surname",max_length=100,null=True, blank=True)
    forget_password_token = models.CharField(max_length=100, blank=True, null=True)
    about = models.TextField("About", max_length=1000, null=True, blank=True)
    profile_img = models.ImageField("Profile image",upload_to='profile_images', default='blank-profile-photo.jpeg')
    location = models.CharField("Location",max_length=100,null=True, blank=True)
    favorites_port = models.ManyToManyField("Portfolio")
    favorites_skelb = models.ManyToManyField("Skelbimas")

    def __str__(self):
        return f'{self.id} {self.user.username}'


class Portfolio(models.Model):
    name = models.CharField("Name",max_length=100, null=True,blank=True)
    about = models.CharField("About",max_length=100,null=True, blank=True)
    area = models.CharField("Area",max_length=100,null=True, blank=True)
    user_id = models.ForeignKey("Profile", on_delete=models.CASCADE)
    cover = models.ImageField("Cover", default='blank-profile-photo.jpeg', upload_to='covers', null=True)
    nr_of_likes = models.IntegerField(default=0)
    is_like = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f'{self.id} {self.name}'

    class Meta:
        ordering = ["-date"]

class Images(models.Model):
    image = models.ImageField("Image", upload_to='portfolio_image', null=True, blank=True)
    portfolio_id = models.ForeignKey("Portfolio", on_delete=models.CASCADE)

class Skelbimas(models.Model):
    logo = models.ImageField("Logo", default='no-image.png', upload_to='skelbimai', blank=True)
    name = models.CharField("Name",max_length=100, null=True,blank=True)
    about = models.CharField("About",max_length=100,null=True, blank=True)
    upload_date = models.DateField("Upload date",null=True,auto_now=True)
    area = models.CharField("Area",max_length=100, null=True, blank=True)
    user_id = models.ForeignKey("Profile", on_delete=models.CASCADE)
    type = models.CharField("Type",max_length=100,null=True, blank=True)
    salary = models.IntegerField("Salary",null=True, blank=True)
    email = models.CharField("Email",max_length=100,null=True, blank=True)
    location = models.CharField("Location", max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.id} {self.name}'

class Comment(models.Model):
    porfolio = models.ForeignKey("Portfolio", on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date= models.DateTimeField(auto_now_add=True)

    def user_comment_port(sender, instance, *args, **kwargs):
        comment = instance
        porfolio = comment.porfolio
        text_preview = comment.body[:90]
        sender = comment.user


        notify = Notification(portfolio=porfolio, sender=sender,user=porfolio.user_id.user,text_preview=text_preview, notification_type=2)
        notify.save()

    def user_del_comment_port(sender, instance, *args, **kwargs):
        comment = instance
        porfolio = comment.porfolio
        sender = comment.user

        notify = Notification.objects.filter(portfolio=porfolio,user=porfolio.user_id.user, sender=sender, notification_type=2)
        notify.delete()

class Review(models.Model):
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date= models.DateTimeField(auto_now_add=True)

    # def user_comment_port(sender, instance, *args, **kwargs):
    #     comment = instance
    #     porfolio = comment.porfolio
    #     text_preview = comment.body[:90]
    #     sender = comment.user
    #
    #
    #     notify = Notification(portfolio=porfolio, sender=sender,user=porfolio.user_id.user,text_preview=text_preview, notification_type=2)
    #     notify.save()
    #
    # def user_del_comment_port(sender, instance, *args, **kwargs):
    #     comment = instance
    #     porfolio = comment.porfolio
    #     sender = comment.user
    #
    #     notify = Notification.objects.filter(portfolio=porfolio,user=porfolio.user_id.user, sender=sender, notification_type=2)
    #     notify.delete()


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    body = models.TextField(max_length=1000, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def send_message(from_user, to_user, body):
        sender_message = Message(
            user=from_user,
            sender=from_user,
            recipient=to_user,
            body=body,
            is_read=True)
        sender_message.save()

        recipient_message = Message(
            user=to_user,
            sender=from_user,
            body=body,
            recipient=from_user)
        recipient_message.save()

        return sender_message

    def get_messages(user):
        users = []
        messages = Message.objects.filter(user=user).values('recipient').annotate(last=Max('date')).order_by('-last')
        for message in messages:
            users.append({
                'user': User.objects.get(pk=message['recipient']),
                'last': message['last'],
                'unread': Message.objects.filter(user=user, recipient__pk=message['recipient'],is_read=False).count()

            })
        return users

class FollowersCount(models.Model):
    follower = models.CharField("User",max_length=100)
    user = models.CharField("User",max_length=100)


class LikePortfolio(models.Model):
    portfolio_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)


    def __str__(self):
        return f'{self.id} {self.username}'


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_like")
    portfolio = models.ForeignKey("Portfolio", on_delete=models.CASCADE, related_name="post_likes")

    def user_liked_port(sender, instance, *args, **kwargs):
        like = instance
        portfolio = like.portfolio
        sender = like.user
        notify = Notification(portfolio=portfolio, sender=sender,user=portfolio.user_id.user, notification_type=1)
        notify.save()

    def user_unliked_port(sender, instance, *args, **kwargs):
        like = instance
        portfolio = like.portfolio
        sender = like.user
        notify = Notification.objects.filter(portfolio=portfolio, sender=sender, notification_type=1)
        notify.delete()

class Notification(models.Model):
    NOTIFICATION_TYPES = ((1, 'Like'), (2, 'Comment'),(3, 'Follow'))

    portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE, related_name='noti_port', blank=True, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='noti_from_user')
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="noti_to_user")
    notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
    text_preview = models.CharField(max_length=90, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)


post_save.connect(Likes.user_liked_port, sender=Likes)
post_delete.connect(Likes.user_unliked_port, sender=Likes)

post_save.connect(Comment.user_comment_port, sender=Comment)
post_delete.connect(Comment.user_del_comment_port, sender=Comment)