from django.contrib import admin
from .models import Profile, Portfolio, Comment, Message, LikePortfolio, Likes, FollowersCount

# Register your models here.
admin.site.register(Profile)
admin.site.register(Portfolio)
admin.site.register(Comment)
admin.site.register(Message)
admin.site.register(LikePortfolio)
admin.site.register(Likes)
admin.site.register(FollowersCount)

