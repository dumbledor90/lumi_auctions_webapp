from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q, F
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import DeleteView, UpdateView, FormView

from .models import User, Listing, Comment, Bid
from .forms import ListingForm, BidForm, CommentForm


class IndexView(ListView):
    template_name = 'auctions/index.html'
    context_object_name = 'listings'
    paginate_by = 6

    # If there's username provided in url, return the listings by that user
    # Otherwise, return all listings
    def get_queryset(self):
        if username := self.kwargs.get('username'):
            queryset = Listing.objects.filter(Q(active=True), Q(owner__username=username))
        else:
            queryset = Listing.objects.filter(Q(active=True))
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add username to context, so we can display it in the page
        context['username'] = self.kwargs.get('username')
        return context


def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    # Check if current listing in user's watchlist'
    in_watchlist = (
        request.user.watchlist.contains(listing) if request.user.is_authenticated
        else False
    )
    
    if request.method == 'POST':

        # This section is to deal with bidding
        if BidForm.prefix in request.POST:
            comment_form = CommentForm()
            
            bid = Bid(user=request.user, listing=listing)
            bid_form = BidForm(request.POST, instance=bid)
            
            if bid_form.is_valid():
                bid_form.save()

                # After saving bid to db, send back the empty form for user to bid more
                bid_form = BidForm()

        # This section is to deal with watchlist
        elif 'watchlist' in request.POST:

            bid_form = BidForm()
            comment_form = CommentForm()

            if in_watchlist:
                request.user.watchlist.remove(listing)
            else:
                request.user.watchlist.add(listing)

            in_watchlist = not in_watchlist
            \
        # This section is to deal with comments
        else:
            bid_form = BidForm()
            
            comment = Comment(user=request.user, listing=listing)
            comment_form = CommentForm(request.POST, instance=comment)

            if comment_form.is_valid():
                comment_form.save()
                # After saving comment to db, send back the empty form for user to add more comments
                comment_form = CommentForm()

    else:
        bid_form = BidForm()
        comment_form = CommentForm()

    # Return the last user who bid on the item, then display it on the page for that user
    # when they visit the page
    lastest_bidder = (listing.bid_set.first().user if listing.bid_count > 0 
                      else None)
    
    comments = Comment.objects.filter(Q(listing=listing))

    return render(request, 'auctions/listing_detail.html', {
        'bid_form': bid_form,
        'comment_form': comment_form,
        'listing': listing,
        'lastest_bidder': lastest_bidder,
        'comments': comments,
        'in_watchlist': in_watchlist,
    })


@login_required(login_url=reverse_lazy('login'))
def create_listing(request):
    if request.method == 'POST':
        listing = Listing(owner=request.user, price=request.POST['start_price'])
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = ListingForm()
    return render(request, 'auctions/listing_form.html', {'form': form})


@login_required(login_url=reverse_lazy('login'))
def close_listing(request, pk):

    listing = get_object_or_404(Listing, pk=pk)
    
    if request.method == 'POST':
        listing.active = False
        listing.save()
        return HttpResponseRedirect(reverse('listing-detail', kwargs={'pk': pk}))

    if request.user != listing.owner:
        raise PermissionDenied
    
    return render(request, 'auctions/listing_confirm_close.html', {'listing': listing})


class ListingUpdateView(UserPassesTestMixin, UpdateView):
    model = Listing
    form_class = ListingForm

    # Only creator of current listing can update it
    def test_func(self):
        self.object = Listing.objects.get(pk=self.kwargs['pk'])
        return self.object.owner == self.request.user


class ListingDeleteView(UserPassesTestMixin, DeleteView):
    model = Listing
    success_url = reverse_lazy('index')
    login_url = reverse_lazy('login')

    # Only creator of current listing can delete it
    def test_func(self):
        self.object = Listing.objects.get(pk=self.kwargs['pk'])
        return self.object.owner == self.request.user
    

class WatchlistView(ListView):
    template_name = 'auctions/index.html'
    context_object_name = 'listings'
    paginate_by = 6

    def get_queryset(self):
        return self.request.user.watchlist.filter(Q(active=True))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Because this view use the same template as index, so use this flag to display appropriate 
        # header element on the page
        context['is_watchlist'] = True
        
        return context
    

def category_view(request, category_name=''):

    listings = Listing.objects.filter(Q(active=True))
    
    if category_name:
        listings = listings.filter(Q(category=category_name))

    paginator = Paginator(listings, 6)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'auctions/categories.html', {
        'categories': Listing.CATEGORIES,
        'listings': listings,
        'selected': category_name,
        'page_obj': page_obj,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
