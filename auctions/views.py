from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone  # Import timezone module
from django.contrib import messages
from .models import User, Listing, Watchlist, Comment
from .form import ListingForm , CommentForm,BidForm


def index(request):
    active_listings = Listing.objects.all()  # Fetch all active listings from the database
    return render(request, "auctions/index.html",  {'active_listings': active_listings})


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
    



def active_listings(request):
    active_listings = Listing.objects.all()  # Fetch all active listings from the database
    return render(request, 'auctions/active_listings.html', {'active_listings': active_listings})




@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creator = request.user
            #listing.starting_bid = listing.current_price  # Set starting bid to current price
            listing.current_price = form.cleaned_data['starting_bid']  # Set current price to starting bid
            listing.created_at = timezone.now()  # Set created_at to current timestamp
            listing.save()
            listing.save()
            return redirect('index')
    else:
        form = ListingForm()
    return render(request, 'auctions/create_listing.html', {'form': form})

@login_required
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    bid_form = BidForm()
    comment_form = CommentForm()
    return render(request, 'auctions/listing_detail.html', {'listing': listing, 'bid_form': bid_form, 'comment_form': comment_form})



@login_required
def place_bid(request, listing_id):
    # Get the listing object or return a 404 response if it doesn't exist
    listing = get_object_or_404(Listing, pk=listing_id)
    
    if request.method == 'POST':
        # Create a bid form instance with POST data
        form = BidForm(request.POST)
        
        # Check if the form data is valid
        if form.is_valid():
            # Save the bid form but do not commit to the database yet
            bid = form.save(commit=False)
            
            # Associate the bid with the listing and the bidder
            bid.listing = listing
            bid.bidder = request.user
            
            # Save the bid to the database
            bid.save()
            
            # Update the current price of the listing
            listing.current_price = bid.bid_amount
            listing.save()
            
            # Redirect to the listing detail page
            return redirect('listing_detail', listing_id=listing_id)
        else:
            # Handle invalid form submission
            return HttpResponse("Error processing bid form.")
    else:
        # Handle GET request (unlikely scenario)
        return HttpResponse("Invalid request method.")






def category_listings(request, category):
    category_listings = Listing.objects.filter(category=category, active=True)
    return render(request, 'auctions/category_listings.html', {'category_listings': category_listings, 'category': category})


def category_listings(request, category_id):
    # Retrieve listings belonging to the specified category
    listings = Listing.objects.filter(category_id=category_id)
    return render(request, 'auctions/category_listings.html', {'listings': listings})




#------------------------------------------------------------------------------------------------------------------------------


#@login_required
#def watchlist(request):
 #   if request.method == 'POST':
  #      listing_id = request.POST.get('listing_id')
 #       listing = get_object_or_404(Listing, pk=listing_id)
   #     request.user.watchlist.listings.add(listing)
  #      print(request.user.watchlist.listings.all())  # This will print the watchlist contents to the console
 #       return redirect('watchlist')
  #  else:
  #      if request.user.is_authenticated:
  #          watchlist_listings = request.user.watchlist.listings.all()
   #         return render(request, 'auctions/watchlist.html', {'watchlist': watchlist_listings})
   #     else:
   #         return render(request, 'auctions/watchlist.html')
#------------------------------------------------------------------------------------------------------------
        
@login_required
def watchlist(request):
    if request.method == 'POST':
        # Handle POST request if necessary
        pass
    else:
        if request.user.is_authenticated:
            watchlist_listings = request.user.watchlist.listings.all()
            # Print watchlist_listings to verify contents
            print(watchlist_listings)
            # Add any additional context data you need
            return render(request, 'auctions/watchlist.html', {'watchlist': watchlist_listings})
        else:
            return render(request, 'auctions/watchlist.html')


from django.contrib import messages

@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    user = request.user
    watchlist = Watchlist.objects.get_or_create(user=user)[0]
    
    if listing in watchlist.listings.all():
        messages.warning(request, 'Listing is already in your watchlist.')
    else:
        watchlist.listings.add(listing)
        messages.success(request, 'Listing added to watchlist successfully.')
    
    return redirect('watchlist')


@login_required
def remove_from_watchlist(request, listing_id):
    # Retrieve the listing from the database
    listing = get_object_or_404(Listing, pk=listing_id)
    
    # Check if the listing exists in the user's watchlist
    if request.user.watchlist.listings.filter(pk=listing_id).exists():
        # Remove the listing from the user's watchlist
        request.user.watchlist.listings.remove(listing)
        return redirect('watchlist')
    else:
        # If the listing is not in the watchlist, display an error message
        # You can customize this error message as needed
        return render(request, 'auctions/error.html', {'error_message': 'Listing is not in your watchlist.'})




from .models import AuctionListing

@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    auction_listing = AuctionListing.objects.get(pk=listing_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.auction_listing = auction_listing  # Set the auction_listing field to the appropriate AuctionListing object
            comment.commenter = request.user
            comment.save()
            return redirect('listing_detail', listing_id=listing_id)
    else:
        return redirect('index')  # Handle GET request or any other cases where the form isn't submitted

