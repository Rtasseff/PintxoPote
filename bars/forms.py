from django import forms
from .models import Bar, BarPhoto


class BarForm(forms.ModelForm):
    class Meta:
        model = Bar
        fields = [
            'name', 'address', 'notes', 'map_link', 'specialties',
            'price_range', 'cana_price', 'crowd_level', 'last_visited', 'tags'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700'}),
            'notes': forms.Textarea(attrs={'rows': 5, 'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700'}),
            'map_link': forms.URLInput(attrs={'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700'}),
            'specialties': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700'}),
            'price_range': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700'}),
            'cana_price': forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700'}),
            'crowd_level': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700'}),
            'last_visited': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700'}),
            'tags': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700', 'placeholder': 'traditional, modern, tapas, etc.'}),
        }


class QuickNoteForm(forms.Form):
    note = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700',
            'placeholder': 'Add a quick note about your visit...'
        }),
        label='Quick Note'
    )


class QuickPhotoForm(forms.ModelForm):
    class Meta:
        model = BarPhoto
        fields = ['image', 'caption', 'is_featured']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700', 'accept': 'image/*'}),
            'caption': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-700', 'placeholder': 'Describe this photo...'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-yellow-600 bg-gray-100 border-gray-300 rounded focus:ring-yellow-500 focus:ring-2'}),
        }