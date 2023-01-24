from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.db.models import Q

from .forms import CommentForm, PostForm, ProfileEditForm, UserEditForm
from .models import Comment, Follow, Group, Message, Post, Profile, User

POSTS_PER_PAGE = 10


@login_required
def follow_index(request):
    post_list = (
        Post.objects.filter(author__following__user=request.user)
        .select_related('group')
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        'post_list': post_list,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    user = User.objects.get(username=request.user.username)
    if author == user:
        return redirect('posts:profile', username)
    Follow.objects.get_or_create(author=author, user=user)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    user = User.objects.get(username=request.user.username)
    Follow.objects.filter(author=author, user=user).delete()
    return redirect('posts:profile', username)


@login_required
def add_like(request, pk, *args, **kwargs):
    post = Post.objects.get(pk=pk)
    is_dislike = False
    for dislike in post.dislikes.all():
        if dislike == request.user:
            is_dislike = True
            break
    if is_dislike:
        post.dislikes.remove(request.user)
    is_like = False
    for like in post.likes.all():
        if like == request.user:
            is_like = True
            break
    if not is_like:
        post.likes.add(request.user)
    if is_like:
        post.likes.remove(request.user)
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def add_dislike(request, pk, *args, **kwargs):
    post = Post.objects.get(pk=pk)
    is_like = False
    for like in post.likes.all():
        if like == request.user:
            is_like = True
            break
    if is_like:
        post.likes.remove(request.user)
    is_dislike = False
    for dislike in post.dislikes.all():
        if dislike == request.user:
            is_dislike = True
            break
    if not is_dislike:
        post.dislikes.add(request.user)
    if is_dislike:
        post.dislikes.remove(request.user)
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
        return redirect('posts:index')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        return render(request,
                      'posts/edit_profile.html',
                      {'user_form': user_form,
                       'profile_form': profile_form})


def comment_post(request, post_id,):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_edit(request, post_id):
    is_edit = True
    template = 'forms/comment_form.html'
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    if user != post.author:
        return redirect('posts:post_detail', post.id)
    if request.method == "POST":
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('posts:post_detail', post.id)
        return render(request, template, {'form': form})
    form = PostForm(instance=post)
    context = {
        'form': form,
        'post': post,
        'is_edit': is_edit,
    }
    return render(request, template, context)


def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    if user != post.author:
        return redirect('posts:post_detail', post.id)
    post.delete()
    return redirect('posts:index')


@login_required
def post_create(request):
    template = 'forms/comment_form.html'
    if request.method == "POST":
        form = PostForm(request.POST or None, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
        return render(request, template, {'form': form})
    form = PostForm()
    return render(request, template, {'form': form})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    template = 'posts/profile.html'
    name = Profile.objects.filter(user=user)
    following = (
        request.user.is_authenticated
        and user.following.filter(user=request.user).exists()
    )
    posts = user.posts.all()
    post_count = Post.objects.filter(author=user).count()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'following': following,
        'name': name,
        'post_count': post_count,
        'author': user,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment = Comment.objects.select_related('author').filter(post_id=post)
    comment_form = CommentForm(data=request.POST or None)
    post_count = post.author.posts.count()
    context = {
        'comment': comment,
        'comment_form': comment_form,
        'post_count': post_count,
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


def index(request):
    posts = Post.objects.select_related('author', 'group')
    comment_form = CommentForm(data=request.POST or None)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    context = {
        'comment_form': comment_form,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.select_related('author')
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def inbox(request):
    messages = Message.get_messages(user=request.user)
    active_direct = None
    directs = None

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(
            user=request.user,
            recipient=message['user']
        )
        directs.update(is_read=True)
        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0

    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
    }

    template = loader.get_template('direct/direct.html')

    return HttpResponse(template.render(context, request))


@login_required
def user_search(request):
    query = request.GET.get("q")
    context = {}
    if query:
        users = User.objects.filter(Q(username__icontains=query))
        paginator = Paginator(users, 6)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)
        context = {
            'users': users_paginator,
        }
    template = loader.get_template('direct/search_user.html')
    return HttpResponse(template.render(context, request))


@login_required
def directs(request, username):
    user = request.user
    messages = Message.get_messages(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, recipient__username=username)
    directs.update(is_read=True)
    users = User.objects.get(username=username)
    image = Profile.objects.filter(user=users)
    print(image)
    for message in messages:
        if message['user'].username == username:
            message['unread'] = 0

    context = {
        'image': image,
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
    }

    template = loader.get_template('direct/direct.html')

    return HttpResponse(template.render(context, request))


@login_required
def new_conversation(request, username):
    from_user = request.user
    body = ''
    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect('posts:usersearch')
    if from_user != to_user:
        Message.send_message(from_user, to_user, body)
    return redirect('posts:inbox')


@login_required
def send_direct(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')
    if request.method == 'POST':
        to_user = User.objects.get(username=to_user_username)
        Message.send_message(from_user, to_user, body)
        return redirect('posts:inbox')
    else:
        HttpResponseBadRequest()


def check_directs(request):
    directs_count = 0
    if request.user.is_authenticated:
        directs_count = Message.objects.filter(
            user=request.user,
            is_read=False).count()
    return {'directs_count': directs_count}
