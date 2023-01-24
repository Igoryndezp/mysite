from django.contrib import admin

from .models import Comment, Group, Post, Profile, Message


class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient']


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'profile_photo', 'instagram']


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'image',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'created',
        'active',
    )
    list_filter = (
        'active',
        'created',
        'updated',
    )
    search_fields = (
        'author',
        'body',
    )


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'slug',
        'description',
    )
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Message, MessageAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
