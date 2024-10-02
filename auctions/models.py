import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.shortcuts import reverse
from django.core.exceptions import ValidationError


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing')


class Listing(models.Model):
    CATEGORIES = {
        'uncategorized': 'uncategorized',
        'family': 'family',
        'personal': 'personal',
    }
    
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    start_price = models.FloatField(default=0)
    bid_count = models.PositiveIntegerField(default=0)
    price = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)
    last_bid_at = models.DateTimeField(auto_now=True)
    image_url = models.URLField()
    active = models.BooleanField(default=True)
    category = models.CharField(max_length=50, choices=CATEGORIES, default='uncategorized')

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')

    class Meta:
        ordering = ['-last_bid_at']

    def __str__(self):
        return f'{self.title} at {self.price} (user {self.owner})'

    @property
    def how_long(self):
        t = timezone.now() - self.updated_at
        if t.days > 7:
            return f'{int(t.days/7)} weeks'
        elif t.days > 0:
            return f'{t.days} days'
        elif t.seconds > 3600:
            return f'{int(t.seconds/3600)} hours'
        elif t.seconds > 60:
            return f'{int(t.seconds/60)} minutes'
        else:
            return f'{t.seconds} seconds'

    def get_absolute_url(self):
        return reverse('listing-detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} "{self.content[:100]}"'
    
    @property
    def how_long(self):
        t = timezone.now() - self.created_at
        if t.days > 7:
            return f'{int(t.days/7)} weeks'
        elif t.days > 0:
            return f'{t.days} days'
        elif t.seconds > 3600:
            return f'{int(t.seconds/3600)} hours'
        elif t.seconds > 60:
            return f'{int(t.seconds/60)} minutes'
        else:
            return f'{t.seconds} seconds'


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    bid_price = models.FloatField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.bid_price} from user {self.user}'
    
    def clean(self):
        if self.bid_price <= self.listing.price:
            raise ValidationError(
                {'bid_price': 'Bid price must be large then current price.',}
            )
        
    def save(self, **kwargs):
        self.listing.bid_count += 1
        self.listing.price = self.bid_price
        self.listing.save()
        super().save(**kwargs)

