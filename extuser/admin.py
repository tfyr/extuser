from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from extuser.models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'UserProfile'


class UserProfileAdmin(UserAdmin):
    #class Meta:
    #    model = UserProfile
    #    fields = '__all__'

    #form = UserProfileAdminForm

    def __init__(self, *args, **kwargs):
        super(UserProfileAdmin, self).__init__(*args, **kwargs)
        #self.fields['firstname'].widget = ForeignKeyRawIdWidget(UserProfile._meta.get_field("agent_id").rel, admin.site)
#        self.fieldsets = self.fieldsets  #+  ({'fields': ('username', 'password')})
    #    self.fieldsets =self.fieldsets + (("Cart", {'fields': ('cart_id',)}),)


    inlines = (UserProfileInline,)



admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
