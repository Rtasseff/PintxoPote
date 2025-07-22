import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Bar, BarPhoto
from .forms import BarForm, QuickNoteForm, QuickPhotoForm


def is_admin(request):
    """Check if user has admin privileges"""
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
        context['search_query'] = self.request.GET.get('search', '')
        return context


class BarDetailView(DetailView):
    model = Bar
    template_name = 'bars/detail.html'
    context_object_name = 'bar'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = is_admin(self.request)
        context['photos'] = self.object.photos.all()
        return context


class BarCreateView(CreateView):
    model = Bar
    form_class = BarForm
    template_name = 'bars/form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request):
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
            return redirect('bars:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, f'Bar "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


def quick_note(request, pk):
    """Add a quick note to an existing bar"""
    if not is_admin(request):
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
    """Add a quick photo to an existing bar"""
    if not is_admin(request):
        return redirect('bars:detail', pk=pk)
        
    bar = get_object_or_404(Bar, pk=pk)
    
    if request.method == 'POST':
        form = QuickPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.bar = bar
            photo.save()
            messages.success(request, 'Photo added successfully!')
            return redirect('bars:detail', pk=pk)
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
