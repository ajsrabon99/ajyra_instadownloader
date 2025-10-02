from django import forms


class VideoForm(forms.Form):
    video_url = forms.URLField(
        label="Instagram Video/Reel/IGTV URL",
        widget=forms.URLInput(attrs={
            "class": "form-control",
            "placeholder": "Paste Instagram video, reel, or IGTV link here...",
            "required": True,
        })
    )
