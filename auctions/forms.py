from django import forms
from django.core.exceptions import ValidationError
from .views import Listing, Bid, Comment


class ListingForm(forms.ModelForm):
    template_name = "auctions/form_snippet.html"

    class Meta:
        model = Listing
        fields = ['title', 'description', 'start_price', 'image_url', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'start_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Name your price'}),
            'image_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image URL'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError('Price must be positive.')
        return price


class BidForm(forms.ModelForm):
    prefix = 'bid'
    template_name = "auctions/form_snippet.html"
    
    class Meta:
        model = Bid
        fields = ['bid_price']
        widgets = {
            'bid_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Name your price'}),
        }
        labels = {
            'bid_price': '',
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write something about this item...', 'style': 'height: 100px;'})
        }
        labels = {
            'content': ''
        }
