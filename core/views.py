import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Content, Category, Comment, Document
from .forms import ContentForm, CommentForm, DocumentForm
from django.utils.text import slugify
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from django.db import transaction, connection


def home(request):
    return render(request, 'core/home.html')


def content_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    all_contents = Content.objects.all().order_by('-created_at')

    if query:
        all_contents = all_contents.filter(Q(title__icontains=query) | Q(body__icontains=query))
    if category:
        all_contents = all_contents.filter(categories__slug=category)

    paginator = Paginator(all_contents, 9)  # Show 9 contents per page
    page_number = request.GET.get('page')
    contents = paginator.get_page(page_number)
    categories = Category.objects.all()

    selected_content = None
    comments = None  # Initialize comments variable
    
    if request.GET.get('content_id'):
        selected_content = get_object_or_404(Content, id=request.GET.get('content_id'))
        # Get comments for the selected content
        comments = Comment.objects.filter(content=selected_content).order_by('-created_at')
    elif contents:
        selected_content = contents[0]
        # Get comments for the first content if no specific content is selected
        comments = Comment.objects.filter(content=selected_content).order_by('-created_at')

    context = {
        'contents': contents,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'selected_content': selected_content,
        'comments': comments,  # Add comments to the context
    }

    return render(request, 'core/content_list.html', context)


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


@transaction.atomic
@login_required
@permission_required('core.add_content', raise_exception=True)
def create_content(request):
    if request.method == 'POST':
        content_form = ContentForm(request.POST, request.FILES)
        document_form = DocumentForm(request.POST, request.FILES)

        if content_form.is_valid():
            content = content_form.save(commit=False)
            content.author = request.user
            content.is_published = True
            content.published_at = timezone.now()

            # Handle categories
            categories = content_form.cleaned_data.get('categories')
            new_category_name = content_form.cleaned_data.get('new_category')
            if new_category_name:
                category, created = Category.objects.get_or_create(name=new_category_name)
                if categories:
                    categories = list(categories) + [category]
                else:
                    categories = [category]

            # Generate unique slug
            base_slug = slugify(content.title)
            unique_slug = base_slug
            counter = 1
            while Content.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            content.slug = unique_slug

            content.save()
            content_form.save_m2m()  # Save many-to-many relationships

            if categories:
                content.categories.set(categories)

            # Handle document upload
            if 'file' in request.FILES:
                if document_form.is_valid():
                    document = document_form.save(commit=False)
                    document.content = content
                    document.uploaded_by = request.user
                    document.save()
                else:
                    for field, errors in document_form.errors.items():
                        for error in errors:
                            messages.warning(request, f"Document {field}: {error}")

            messages.success(request, 'Content created successfully!')
            return redirect('content_list')
        else:
            for field, errors in content_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            
            # Print form errors to console for debugging
            print("Content Form Errors:", content_form.errors)

        # Handle document form errors
        if document_form.is_bound and not document_form.is_valid():
            for field, errors in document_form.errors.items():
                for error in errors:
                    messages.error(request, f"Document {field.capitalize()}: {error}")
            
            # Print form errors to console for debugging
            print("Document Form Errors:", document_form.errors)

    else:
        content_form = ContentForm()
        document_form = DocumentForm()

    return render(request, 'core/dashboard.html', {
        'content_form': content_form,
        'document_form': document_form,
    })

@login_required
def dashboard(request):
    if request.method == 'POST':
        content_form = ContentForm(request.POST, request.FILES)
        document_form = DocumentForm()  # Initialize document_form
        print("POST data:", request.POST)
        
        # Process content form
        if content_form.is_valid():
            # Save content
            content = content_form.save(commit=False)
            content.author = request.user
            content.is_published = True
            content.published_at = timezone.now()
            content.save()

            # Handle categories
            categories = content_form.cleaned_data.get('categories')
            new_category_name = request.POST.get('new_category')
            category_id = request.POST.get('category')
            
            # Handle new category
            if category_id == 'new' and new_category_name:
                category, _ = Category.objects.get_or_create(name=new_category_name)
                content.categories.add(category)
            # Handle existing category
            elif category_id and category_id != 'new':
                try:
                    category = Category.objects.get(id=int(category_id))
                    content.categories.add(category)
                except (ValueError, Category.DoesNotExist):
                    pass

            # Handle document upload ONLY IF file is provided
            if 'file' in request.FILES and request.FILES['file']:
                document_title = request.POST.get('document_title', '').strip()
                if document_title:
                    document = Document(
                        title=document_title,
                        file=request.FILES['file'],
                        content=content,
                        uploaded_by=request.user
                    )
                    document.save()
                    messages.info(request, f"Document '{document_title}' attached successfully.")
                else:
                    # If no title is provided but a file is uploaded, show error and don't redirect
                    messages.error(request, "Document title is required when uploading a file.")
                    # Return to the form instead of redirecting
                    return render(request, 'core/dashboard.html', {
                        'content_form': ContentForm(request.POST),  # Preserve the form data
                        'document_form': document_form,
                        'categories': Category.objects.all(),
                        'contents': Content.objects.filter(author=request.user).order_by('-created_at')[:5],
                    })

            messages.success(request, 'Content created successfully!')
            return redirect('content_list')
        else:
            print("Form errors:", content_form.errors)
            for field, errors in content_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        content_form = ContentForm()
        document_form = DocumentForm()
    
    categories = Category.objects.all()
    contents = Content.objects.filter(author=request.user).order_by('-created_at')[:5]

    return render(request, 'core/dashboard.html', {
        'content_form': content_form,
        'document_form': document_form,
        'categories': categories,
        'contents': contents,
    })



@login_required
def edit_content(request, slug):
    content = get_object_or_404(Content, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        
        # Store current categories to preserve them if form validation fails
        current_categories = list(content.categories.all())
        
        if form.is_valid():
            updated_content = form.save(commit=False)

            if updated_content.is_published and not content.published_at:
                updated_content.published_at = timezone.now()

            # Save the content first
            updated_content.save()
            
            # Handle categories
            category_id = request.POST.get('category')
            new_category_name = request.POST.get('new_category')
            
            # Clear existing categories if we're going to set new ones
            if (category_id and category_id != 'new') or (category_id == 'new' and new_category_name):
                updated_content.categories.clear()
            
            # Add selected category
            if category_id and category_id != 'new':
                try:
                    category = Category.objects.get(id=int(category_id))
                    updated_content.categories.add(category)
                except (ValueError, Category.DoesNotExist):
                    pass
            
            # Add new category if created
            elif category_id == 'new' and new_category_name:
                category, created = Category.objects.get_or_create(name=new_category_name)
                updated_content.categories.add(category)
            
            # If no categories were added but there were categories before, restore them
            if not updated_content.categories.exists() and current_categories:
                for category in current_categories:
                    updated_content.categories.add(category)

            messages.success(request, 'Content updated successfully!')
            return redirect('content_detail', slug=updated_content.slug)
        else:
            messages.error(request, 'There was an error updating the content. Please check the form.')
            print(form.errors)
    else:
        # For GET requests, pre-populate the form
        initial_data = {}
        if content.categories.exists():
            initial_data['category'] = content.categories.first().id
        
        form = ContentForm(instance=content, initial=initial_data)

    return render(request, 'core/edit_content.html', {'form': form, 'content': content, 'categories': Category.objects.all()})


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
        comment_text = request.POST.get('comment_text')
        if comment_text:
            Comment.objects.create(
                content=content,
                author=request.user,
                body=comment_text
            )
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Comment cannot be empty.')
    
    return redirect('content_detail', slug=slug)


@login_required
def user_profile(request):
    user_contents = Content.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'core/user_profile.html', {'user_contents': user_contents})


def update_content_timestamp(content_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT update_content_modified(%s)", [content_id])