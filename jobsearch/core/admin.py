from django.contrib import admin
from .models import Profile, Portfolio,Review, Comment,Skelbimas, Message, LikePortfolio, Likes, FollowersCount, Notification, Images

# Register your models here.
admin.site.register(Profile)
admin.site.register(Portfolio)
admin.site.register(Skelbimas)
admin.site.register(Comment)
admin.site.register(Message)
admin.site.register(LikePortfolio)
admin.site.register(Likes)
admin.site.register(FollowersCount)
admin.site.register(Notification)
admin.site.register(Images)
admin.site.register(Review)

