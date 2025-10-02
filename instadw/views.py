import os
import tempfile
import threading
import requests
from django.http import HttpResponseBadRequest, FileResponse, StreamingHttpResponse, Http404
from django.shortcuts import render, redirect
from django.utils.encoding import smart_str
from django.views.decorators.http import require_GET
from yt_dlp import YoutubeDL
from .forms import VideoForm
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from .models import ContactMessage


# Default headers (Instagram কিছু ক্ষেত্রে UA চায়)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}

CHUNK_SIZE = 8192  # প্রতি বার 8KB ডাটা stream করবে

def stream_file(url: str):
    """
    External video ফাইল stream করার জন্য generator.
    Headers যুক্ত করে Instagram 403 error কমানো হয়েছে.
    """
    try:
        with requests.get(url, stream=True, timeout=25, headers=HEADERS) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    yield chunk
    except requests.exceptions.HTTPError as e:
        print(f"⚠️ Streaming HTTP error: {e}")
        raise Http404("Instagram video cannot be streamed (403/Forbidden).")
    except Exception as e:
        print(f"⚠️ Streaming error: {e}")
        raise Http404("File stream failed")


def home(request):
    """
    Render home page + handle Instagram video/reel download form
    """
    context = {}
    if request.method == "POST":
        form = VideoForm(request.POST)
        if form.is_valid():
            video_url = form.cleaned_data["video_url"]

            try:
                # Extract video info (without downloading yet)
                ydl_opts = {
                    "quiet": True,
                    "skip_download": True,
                    "http_headers": HEADERS,
                }
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)

                # Pick a playable format (mp4 only)
                best = next(
                    (f for f in reversed(info.get("formats", []))
                     if f.get("ext") == "mp4" and f.get("url")),
                    None
                )

                context.update({
                    "form": form,
                    "video_url": video_url,
                    "info": {
                        "title": info.get("title"),
                        "uploader": info.get("uploader"),
                        "duration": info.get("duration"),
                    },
                    "thumbnail": info.get("thumbnail"),
                    "best": best,
                })

            except Exception as e:
                context["form"] = form
                context["error"] = f"❌ Failed to fetch video: {str(e)}"
        else:
            context["form"] = form
            context["error"] = "Invalid Instagram video URL!"
    else:
        context["form"] = VideoForm()

    return render(request, "instadw/home.html", context)


@require_GET
def play_proxy(request):
    """
    ভিডিও ব্রাউজারে play করাবে (stream করে)।
    Headers যুক্ত করা হয়েছে।
    """
    video_url = request.GET.get("url")
    if not video_url:
        raise Http404("Missing video url")

    return StreamingHttpResponse(
        stream_file(video_url),
        content_type="video/mp4"
    )


@require_GET
def download_proxy(request):
    """
    Direct streaming proxy দিয়ে download করাবে।
    """
    video_url = request.GET.get("url")
    title = request.GET.get("title", "instagram_video")

    if not video_url:
        raise Http404("Missing video url")

    response = StreamingHttpResponse(
        stream_file(video_url),
        content_type="video/mp4"
    )
    response["Content-Disposition"] = f'attachment; filename="{title}.mp4"'
    return response


def download_via_ytdlp(request):
    """
    yt-dlp দিয়ে প্রথমে ফাইল temp ডিরেক্টরিতে ডাউনলোড করবে,
    তারপর FileResponse দিয়ে return করবে (play বা download দুইটাই possible)।
    """
    video_url = request.GET.get("video_url")
    play_inline = request.GET.get("play", "false").lower() == "true"

    if not video_url:
        return HttpResponseBadRequest("Missing video_url parameter.")

    try:
        tmp_dir = tempfile.gettempdir()
        output_path = os.path.join(tmp_dir, "insta_video.%(ext)s")

        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": output_path,
            "merge_output_format": "mp4",
            "http_headers": HEADERS,
            "noplaylist": True,
            "quiet": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            final_file = ydl.prepare_filename(info)

        if not os.path.exists(final_file):
            return HttpResponseBadRequest("⚠️ Failed to download video.")

        response = FileResponse(
            open(final_file, "rb"),
            as_attachment=not play_inline,
            filename=smart_str(info.get("title", "instagram_video") + ".mp4")
        )

        # Cleanup in background
        def cleanup(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"⚠️ Cleanup failed: {e}")

        threading.Thread(target=cleanup, args=(final_file,)).start()

        return response

    except Exception as e:
        return HttpResponseBadRequest(f"Error downloading video: {e}")


def about(request):
    return render(request, "instadw/about.html")

def contact(request):
    context = {}
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not subject or not message:
            context["error"] = "All fields are required."
        else:
            # Save to DB
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            context["success"] = "✅ Your message has been submitted successfully!"

    return render(request, "instadw/contact.html", context)
