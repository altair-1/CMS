from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Content, Category, Comment
from .forms import ContentForm, CommentForm
from django.utils.text import slugify
from django.contrib.auth.decorators import permission_required
from django.utils import timezone


def home(request):
    latest_content = Content.objects.filter(is_published=True).order_by('-published_at')[:5]
    categories = Category.objects.all()
    return render(request, 'core/home.html', {'latest_content': latest_content, 'categories': categories})


def content_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    all_contents = Content.objects.all()  # Allow staff to see all content

    if query:
        all_contents = all_contents.filter(Q(title__icontains=query) | Q(body__icontains=query))
    if category:
        all_contents = all_contents.filter(categories__slug=category)

    all_contents = all_contents.order_by('-created_at')
    paginator = Paginator(all_contents, 9)  # Show 9 contents per page
    page_number = request.GET.get('page')
    contents = paginator.get_page(page_number)
    categories = Category.objects.all()

    return render(request, 'core/content_list.html', {
        'contents': contents,
        'categories': categories,
        'query': query,
        'selected_category': category
    })


def content_detail(request, slug):
    content = get_object_or_404(
        Content.objects.select_related('author').prefetch_related('categories', 'comments'),
        slug=slug
    )
    comment_form = CommentForm()
    return render(request, 'core/content_detail.html', {
        'content': content,
        'comments': content.comments.all(),
        'comment_form': comment_form
    })


@login_required
@permission_required('core.add_content', raise_exception=True)
def create_content(request):
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            content = form.save(commit=False)
            content.author = request.user
            content.is_published = True
            content.published_at = timezone.now() 

            category_choice = form.cleaned_data.get('category')
            new_category_name = form.cleaned_data.get('new_category')

            if category_choice == 'new' and new_category_name:
                category, created = Category.objects.get_or_create(name=new_category_name)
            elif category_choice and category_choice != 'new':
                category = Category.objects.get(id=int(category_choice))
            else:
                category = None

            base_slug = slugify(content.title)
            unique_slug = base_slug
            counter = 1
            while Content.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            content.slug = unique_slug

            content.save()
            if category:
                content.categories.add(category)

            messages.success(request, 'Content created successfully!')
            return redirect('content_detail', slug=content.slug)
        else:
            messages.error(request, 'There was an error creating the content. Please check the form.')
            print(form.errors)
    else:
        form = ContentForm()

    return render(request, 'core/create_content.html', {'form': form})


@login_required
def edit_content(request, slug):
    content = get_object_or_404(Content, slug=slug, author=request.user)
    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            updated_content = form.save(commit=False)

            if updated_content.is_published and not content.published_at:
                updated_content.published_at = timezone.now()

            category_choice = form.cleaned_data.get('category')
            new_category_name = form.cleaned_data.get('new_category')

            if category_choice == 'new' and new_category_name:
                category, created = Category.objects.get_or_create(name=new_category_name)
            elif category_choice and category_choice != 'new':
                category = Category.objects.get(id=int(category_choice))
            else:
                category = None

            updated_content.save()
            if category:
                updated_content.categories.set([category])  # Replace existing categories

            messages.success(request, 'Content updated successfully!')
            return redirect('content_detail', slug=updated_content.slug)
        else:
            messages.error(request, 'There was an error updating the content. Please check the form.')
            print(form.errors)
    else:
        initial_data = {
            'category': content.categories.first().id if content.categories.exists() else None,
        }
        form = ContentForm(instance=content, initial=initial_data)

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
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            print(form.errors)  # For debugging

    return redirect('content_detail', slug=slug)


@login_required
def user_profile(request):
    user_contents = Content.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'core/user_profile.html', {'user_contents': user_contents})