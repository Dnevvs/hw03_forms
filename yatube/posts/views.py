from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .forms import PostForm
from .models import Post, Group, User
from .utils import mypaginator


def index(request):
    post_list = Post.objects.select_related('group')
    page_obj = mypaginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('group').filter(group=group)
    page_obj = mypaginator(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related('group').filter(author=author)
    post_count = post_list.count()
    page_obj = mypaginator(request, post_list)
    context = {
        'author': author,
        'page_obj': page_obj,
        'post_count': post_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_count = post.author.posts.count()
    context = {
        'post': post,
        'post_count': post_count,
        'short_text': post.text[:30]
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    groups = Group.objects.all()
    username = request.user
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = username
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'groups': groups})


@login_required
def post_edit(request, post_id):
    groups = Group.objects.all()
    post = get_object_or_404(Post, id=post_id)
    username = request.user
    if post.author != username:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = username
        post.pub_date = timezone.now()
        post.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'groups': groups,
                   'post_id': post_id, 'is_edit': True})
