import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, FileResponse, Http404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.conf import settings
from .models import Bar, BarPhoto, UserProfile, BarComment
from .forms import BarForm, QuickNoteForm, QuickPhotoForm, CommentForm
import mimetypes


def can_write(request):
    """Check if user has write privileges"""
    if not request.user.is_authenticated:
        return False
    try:
        return request.user.profile.can_write
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        UserProfile.objects.create(user=request.user, can_write=False)
        return False

def is_admin(request):
    """Check if user has admin privileges (legacy token + new user system)"""
    # Check new user system first
    if can_write(request):
        return True
    
    # Fall back to token system for backwards compatibility
    admin_token = os.getenv('ADMIN_TOKEN')
    if not admin_token:
        return False
    return request.session.get('admin_authenticated') or request.GET.get('admin') == admin_token


class BarListView(ListView):
    model = Bar
    template_name = 'bars/home.html'
    context_object_name = 'bars'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Bar.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(specialties__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
        
        # Filter functionality
        price_filter = self.request.GET.get('price_range')
        if price_filter:
            queryset = queryset.filter(price_range=price_filter)
            
        cana_min = self.request.GET.get('cana_min')
        cana_max = self.request.GET.get('cana_max')
        if cana_min:
            queryset = queryset.filter(cana_price__gte=cana_min)
        if cana_max:
            queryset = queryset.filter(cana_price__lte=cana_max)
            
        tags_filter = self.request.GET.get('tags')
        if tags_filter:
            queryset = queryset.filter(tags__icontains=tags_filter)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = is_admin(self.request)
        context['can_write'] = can_write(self.request)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class BarDetailView(DetailView):
    model = Bar
    template_name = 'bars/detail.html'
    context_object_name = 'bar'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = is_admin(self.request)
        context['can_write'] = can_write(self.request)
        context['photos'] = self.object.photos.all()
        context['comments'] = self.object.comments.filter(is_approved=True).select_related('user')
        context['comment_form'] = CommentForm() if self.request.user.is_authenticated else None
        return context


class BarCreateView(CreateView):
    model = Bar
    form_class = BarForm
    template_name = 'bars/form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request):
            messages.error(request, 'You need write permissions to create bars.')
            return redirect('bars:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, f'Bar "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class BarUpdateView(UpdateView):
    model = Bar
    form_class = BarForm
    template_name = 'bars/form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request):
            messages.error(request, 'You need write permissions to edit bars.')
            return redirect('bars:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, f'Bar "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


def quick_note(request, pk):
    """Add a quick note to an existing bar"""
    if not is_admin(request):
        messages.error(request, 'You need write permissions to add notes.')
        return redirect('bars:detail', pk=pk)
        
    bar = get_object_or_404(Bar, pk=pk)
    
    if request.method == 'POST':
        form = QuickNoteForm(request.POST)
        if form.is_valid():
            new_note = form.cleaned_data['note']
            if bar.notes:
                bar.notes += f"\n\n{new_note}"
            else:
                bar.notes = new_note
            bar.save()
            messages.success(request, 'Quick note added successfully!')
            return redirect('bars:detail', pk=pk)
    else:
        form = QuickNoteForm()
    
    return render(request, 'bars/quick_note.html', {
        'form': form,
        'bar': bar
    })


def quick_photo(request, pk):
    """Add a quick photo to an existing bar (any authenticated user)"""
    if not request.user.is_authenticated:
        messages.error(request, 'You need to be logged in to add photos.')
        return redirect('bars:detail', pk=pk)
        
    bar = get_object_or_404(Bar.objects.prefetch_related('photos'), pk=pk)
    
    if request.method == 'POST':
        form = QuickPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.bar = bar
            photo.uploaded_by = request.user
            photo.save()
            messages.success(request, 'Photo added successfully!')
            return redirect('bars:detail', pk=pk)
        else:
            # Re-add error message to help debug
            messages.error(request, 'Please check the form and try again.')
    else:
        form = QuickPhotoForm()
    
    return render(request, 'bars/quick_photo.html', {
        'form': form,
        'bar': bar
    })


def admin_login(request):
    """Simple admin token authentication"""
    admin_token = request.GET.get('admin')
    if admin_token and admin_token == os.getenv('ADMIN_TOKEN'):
        request.session['admin_authenticated'] = True
        messages.success(request, 'Admin access granted!')
    return redirect('bars:home')


def user_login(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('bars:home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'bars/login.html', {'form': form})


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('bars:home')


def user_register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile with default permissions
            UserProfile.objects.create(user=user, can_write=False)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('bars:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'bars/register.html', {'form': form})


def photo_management(request, pk):
    """Photo management view for a specific bar"""
    if not is_admin(request):
        messages.error(request, 'You need write permissions to manage photos.')
        return redirect('bars:detail', pk=pk)
        
    bar = get_object_or_404(Bar.objects.prefetch_related('photos'), pk=pk)
    photos = bar.photos.all()
    
    return render(request, 'bars/photo_management.html', {
        'bar': bar,
        'photos': photos
    })


def delete_photo(request, photo_id):
    """Delete a specific photo"""
    if not is_admin(request):
        messages.error(request, 'You need write permissions to delete photos.')
        return redirect('bars:home')
        
    photo = get_object_or_404(BarPhoto, id=photo_id)
    bar_pk = photo.bar.pk
    
    if request.method == 'POST':
        photo_name = f"Photo for {photo.bar.name}"
        if photo.caption:
            photo_name += f" ({photo.caption})"
        photo.delete()  # This will trigger our custom delete method
        messages.success(request, f'{photo_name} deleted successfully!')
        
        # Redirect back to where they came from
        next_url = request.POST.get('next', 'bars:detail')
        if next_url == 'bars:photo_management':
            return redirect('bars:photo_management', pk=bar_pk)
        else:
            return redirect('bars:detail', pk=bar_pk)
    
    return render(request, 'bars/delete_photo_confirm.html', {
        'photo': photo,
        'bar': photo.bar
    })


def add_comment(request, pk):
    """Add a comment to a bar (any authenticated user)"""
    if not request.user.is_authenticated:
        messages.error(request, 'You need to be logged in to leave a comment.')
        return redirect('bars:detail', pk=pk)
        
    bar = get_object_or_404(Bar, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.bar = bar
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('bars:detail', pk=pk)
        else:
            messages.error(request, 'Please check your comment and try again.')
    
    return redirect('bars:detail', pk=pk)


# Media file serving for Railway production
def serve_media(request, path):
    """Serve media files directly in production"""
    try:
        file_path = settings.MEDIA_ROOT / path
        if file_path.exists() and file_path.is_file():
            content_type, _ = mimetypes.guess_type(str(file_path))
            return FileResponse(
                open(file_path, 'rb'),
                content_type=content_type,
                as_attachment=False
            )
        else:
            raise Http404(f"Media file not found: {path}")
    except Exception as e:
        raise Http404(f"Error serving media: {str(e)}")
