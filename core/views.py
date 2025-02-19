from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Content, Category
from .forms import ContentForm

def home(request):
    latest_content = Content.objects.filter(is_published=True).order_by('-published_at')[:5]
    return render(request, 'core/home.html', {'latest_content': latest_content})

def content_list(request):
    contents = Content.objects.filter(is_published=True).order_by('-published_at')
    return render(request, 'core/content_list.html', {'contents': contents})

def content_detail(request, slug):
    content = get_object_or_404(Content, slug=slug, is_published=True)
    return render(request, 'core/content_detail.html', {'content': content})

@login_required
def create_content(request):
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            content = form.save(commit=False)
            content.author = request.user
            content.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('content_detail', slug=content.slug)
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
            return redirect('content_detail', slug=content.slug)
    else:
        form = ContentForm(instance=content)
    return render(request, 'core/edit_content.html', {'form': form, 'content': content})

@login_required
def delete_content(request, slug):
    content = get_object_or_404(Content, slug=slug, author=request.user)
    if request.method == 'POST':
        content.delete()
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
            return redirect('content_detail', slug=slug)
    return redirect('content_detail', slug=slug)