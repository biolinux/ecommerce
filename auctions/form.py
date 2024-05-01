# forms.py

from django import forms
from .models import Listing, Bid,Comment

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image_url','image', 'category']

    def clean_starting_bid(self):
        starting_bid = self.cleaned_data.get('starting_bid')
        if starting_bid <= 0:
            raise forms.ValidationError("Starting bid must be greater than zero.")
        return starting_bid


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_amount']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text']