from django import forms
from django.core.files.uploadedfile import UploadedFile
from PIL import Image

from .models import Category, Product, Store

MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_FORMATS = {'PNG', 'JPEG', 'WEBP'}


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'price',
            'stock',
            'description',
            'category',
            'image',
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'price': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01'}
            ),
            'stock': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0'}
            ),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if not isinstance(image, UploadedFile):
            return image

        if image.size > MAX_IMAGE_SIZE:
            raise forms.ValidationError(
                'Image must be smaller than 5 MB.'
            )

        try:
            with Image.open(image) as probe:
                probe.verify()
            image.seek(0)
            with Image.open(image) as probe:
                detected_format = probe.format
        except Exception as error:
            raise forms.ValidationError(
                'Uploaded file is not a valid image.'
            ) from error

        if detected_format not in ALLOWED_IMAGE_FORMATS:
            raise forms.ValidationError(
                'Only PNG, JPEG, and WebP images are allowed.'
            )

        image.seek(0)
        return image


class ProductSearchForm(forms.Form):
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Search products...'}
        )
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All categories'
    )
