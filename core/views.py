from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Content, Category, Comment
from .forms import ContentForm, CommentForm
from django.utils.text import slugify


def home(request):
    latest_content = Content.objects.filter(is_published=True).order_by('-published_at')[:5]
    categories = Category.objects.all()
    return render(request, 'core/home.html', {'latest_content': latest_content, 'categories': categories})

def content_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    all_contents = Content.objects.filter(is_published=True)
    
    if query:
        all_contents = all_contents.filter(Q(title__icontains=query) | Q(body__icontains=query))
    if category:
        all_contents = all_contents.filter(categories__slug=category)
    
    all_contents = all_contents.order_by('-created_at')
    paginator = Paginator(all_contents, 9)  # Show 9 contents per page
    page_number = request.GET.get('page')
    contents = paginator.get_page(page_number)
    categories = Category.objects.all()
    return render(request, 'core/content_list.html', {'contents': contents, 'categories': categories, 'query': query, 'selected_category': category})

def content_detail(request, slug):
    content = get_object_or_404(Content, slug=slug, is_published=True)
    comments = content.comments.filter(is_approved=True)
    comment_form = CommentForm()
    return render(request, 'core/content_detail.html', {'content': content, 'comments': comments, 'comment_form': comment_form})

@login_required
def create_content(request):
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            content = form.save(commit=False)
            content.author = request.user
            content.slug = slugify(content.title)
            if Content.objects.filter(slug=content.slug).exists():
                count = 1
                while Content.objects.filter(slug=f"{content.slug}-{count}").exists():
                    count += 1
                content.slug = f"{content.slug}-{count}"
            content.save()
            form.save_m2m()  # save many-to-many relationships
            messages.success(request, 'Content created successfully!')
            return redirect('content_detail', slug=content.slug)
        else:
            messages.error(request, 'There was an error creating the content. Please check the form.')
    else:
        form = ContentForm()
    return render(request, 'core/create_content.html', {'form': form})

@login_required
def edit_content(request, slug):
    content = get_object_or_404(Content, slug=slug, author=request.user)
    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, 'Content updated successfully!')
            return redirect('content_detail', slug=content.slug)
    else:
        form = ContentForm(instance=content)
    return render(request, 'core/edit_content.html', {'form': form, 'content': content})

@login_required
def delete_content(request, slug):
    content = get_object_or_404(Content, slug=slug, author=request.user)
    if request.method == 'POST':
        content.delete()
        messages.success(request, 'Content deleted successfully!')
        return redirect('content_list')
    return render(request, 'core/delete_content.html', {'content': content})

@login_required
def add_comment(request, slug):
    content = get_object_or_404(Content, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.content = content
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added and is awaiting approval.')
        else:
            messages.error(request, 'There was an error with your comment. Please try again.')
    return redirect('content_detail', slug=slug)

@login_required
def user_profile(request):
    user_contents = Content.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'core/user_profile.html', {'user_contents': user_contents})