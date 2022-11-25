from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
# from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .forms import PostForm
from django.utils import timezone


User = get_user_model()

POSTS_AMOUNT: int = 10


def mypaginator(request, post_list):
    paginator = Paginator(post_list, POSTS_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


# @login_required
def index(request):
    post_list = Post.objects.select_related('group')
    page_obj: Paginator = mypaginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('group').filter(group=group)
    page_obj: Paginator = mypaginator(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related('group').filter(author=author)
    post_count = post_list.count()
    page_obj: Paginator = mypaginator(request, post_list)
    context = {
        'author': author,
        'post_list': post_list,
        'page_obj': page_obj,
        'post_count': post_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_count = (Post.objects.select_related('group').
                  filter(author=post.author).count())
    context = {
        'post': post,
        'post_count': post_count,
        'short_text': post.text[:30]
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    groups = Group.objects.all()
    username = request.user
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = username
            post.text = form.cleaned_data['text']
            post.group = form.cleaned_data['group']
            post.save()
            return redirect(f'/profile/{username}/')
        return render(request, 'posts/create_post.html',
                      {'form': form, 'groups': groups})
    form = PostForm()
    return render(request, 'posts/create_post.html',
                  {'form': form, 'groups': groups})


def post_edit(request, post_id):
    groups = Group.objects.all()
    post = get_object_or_404(Post, id=post_id)
    username = request.user
    if post.author == username:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = username
                post.pub_date = timezone.now()
                post.text = form.cleaned_data['text']
                post.group = form.cleaned_data['group']
                post.save()
                return redirect(f'/posts/{post_id}/')
        else:
            form = PostForm(instance=post)
            return render(request, 'posts/create_post.html',
                          {'form': form, 'groups': groups,
                           'post_id': post_id, 'is_edit': True})
        return redirect(f'/posts/{post_id}/')
