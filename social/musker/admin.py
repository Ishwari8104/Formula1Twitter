from django.contrib import admin
from django.contrib.auth.models import Group,User
from .models import Profile,Tweet
# Register your models here.
#unregister groups
admin.site.unregister(Group)
#extend user model
class ProfileInLine(admin.StackedInline):
    model=Profile
class UserAdmin(admin.ModelAdmin):
    model=User
    fields = ['username']
    inlines=[ProfileInLine]
    
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
#admin.site.register(Profile)
#Mix profile info with user info 
admin.site.register(Tweet)
