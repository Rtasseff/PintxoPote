import os
import tarfile
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import Bar, BarPhoto, UserProfile, BarComment
from .forms import BarForm, QuickNoteForm, QuickPhotoForm, CommentForm


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


# TEMPORARY: Railway Data Upload View - REMOVE AFTER USE
@csrf_exempt
def railway_upload(request):
    """Temporary view to upload data archive to Railway"""
    if request.method == 'POST' and 'data_archive' in request.FILES:
        uploaded_file = request.FILES['data_archive']
        
        # More flexible file type checking
        valid_extensions = ['.tar.gz', '.tgz', '.tar', '.gz']
        if not any(uploaded_file.name.endswith(ext) for ext in valid_extensions):
            messages.error(request, f'Please upload a tar.gz file. Got: {uploaded_file.name}')
            return render(request, 'bars/railway_upload.html')
        
        try:
            # Save uploaded file temporarily
            temp_path = f'/tmp/{uploaded_file.name}'
            with open(temp_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Extract to /app (Railway volume mount parent)
            if hasattr(settings, 'DATA_DIR'):
                extract_path = settings.DATA_DIR.parent  # /app (parent of /app/data)
            else:
                extract_path = '/app'
            
            # Try different tar modes
            try:
                with tarfile.open(temp_path, 'r:gz') as tar:
                    tar.extractall(path=extract_path)
            except tarfile.ReadError:
                with tarfile.open(temp_path, 'r:*') as tar:  # Auto-detect format
                    tar.extractall(path=extract_path)
            
            # Clean up temp file
            os.remove(temp_path)
            
            # Verify extraction worked
            data_path = os.path.join(extract_path, 'data')
            if os.path.exists(data_path):
                db_path = os.path.join(data_path, 'db.sqlite3')
                uploads_path = os.path.join(data_path, 'uploads')
                status = f'✅ Data extracted to {extract_path}!'
                if os.path.exists(db_path):
                    status += f' Database found: {os.path.getsize(db_path)} bytes.'
                if os.path.exists(uploads_path):
                    photo_count = len([f for f in os.listdir(os.path.join(uploads_path, 'bars')) if f.endswith('.jpg')])
                    status += f' Found {photo_count} photos.'
                messages.success(request, status)
            else:
                messages.warning(request, f'Archive extracted but data/ folder not found in {extract_path}')
            
            return redirect('bars:home')
            
        except Exception as e:
            messages.error(request, f'Upload failed: {str(e)}')
            # Clean up on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    # Add debug info for troubleshooting
    context = {
        'debug_info': {
            'method': request.method,
            'has_files': bool(request.FILES),
            'csrf_token': request.META.get('CSRF_COOKIE', 'Not found'),
        }
    }
    return render(request, 'bars/railway_upload.html', context)


# TEMPORARY: Debug view to check file system
@csrf_exempt
def debug_files(request):
    """Debug view to check file paths and existence"""
    debug_info = {}
    
    try:
        debug_info['DATA_DIR'] = str(settings.DATA_DIR) if hasattr(settings, 'DATA_DIR') else 'Not set'
        debug_info['MEDIA_ROOT'] = str(settings.MEDIA_ROOT)
        debug_info['MEDIA_URL'] = settings.MEDIA_URL
        
        # Check if data directory exists
        if hasattr(settings, 'DATA_DIR'):
            try:
                data_dir = settings.DATA_DIR
                debug_info['data_dir_exists'] = data_dir.exists()
                if data_dir.exists():
                    debug_info['data_dir_contents'] = [str(p) for p in data_dir.iterdir()]
            except Exception as e:
                debug_info['data_dir_error'] = str(e)
        
        # Check media root
        try:
            media_root = settings.MEDIA_ROOT
            debug_info['media_root_exists'] = media_root.exists()
            if media_root.exists():
                debug_info['media_root_contents'] = [str(p) for p in media_root.iterdir()]
                
                # Check bars subfolder
                bars_path = media_root / 'bars'
                debug_info['bars_path_exists'] = bars_path.exists()
                if bars_path.exists():
                    jpg_files = list(bars_path.glob('*.jpg'))
                    debug_info['bars_files_count'] = len(jpg_files)
                    debug_info['first_5_files'] = [str(f) for f in jpg_files[:5]]
        except Exception as e:
            debug_info['media_root_error'] = str(e)
        
        # Check database photos
        try:
            from .models import BarPhoto
            photos = BarPhoto.objects.all()[:5]
            debug_info['db_photos'] = []
            for photo in photos:
                photo_info = {
                    'id': photo.id,
                    'image_path': str(photo.image) if photo.image else 'No image',
                    'bar_name': photo.bar.name,
                }
                if photo.image:
                    try:
                        full_path = settings.MEDIA_ROOT / photo.image.name
                        photo_info['full_path'] = str(full_path)
                        photo_info['file_exists'] = full_path.exists()
                    except Exception as e:
                        photo_info['path_error'] = str(e)
                debug_info['db_photos'].append(photo_info)
        except Exception as e:
            debug_info['db_photos_error'] = str(e)
            
    except Exception as e:
        debug_info['general_error'] = str(e)
    
    return render(request, 'bars/debug.html', {'debug_info': debug_info})
