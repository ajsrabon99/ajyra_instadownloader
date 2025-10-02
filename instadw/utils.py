from typing import Dict, Any, List, Optional
import os
import yt_dlp

# Timeout (default 25s, .env থেকে override করতে পারো)
REQUEST_TIMEOUT = int(os.getenv('REQUESTS_TIMEOUT', '25'))

# yt-dlp default options
YDL_OPTS_BASE = {
    "quiet": True,
    "skip_download": True,   # প্রথমে শুধু metadata আনবে
    "nocheckcertificate": True,
    "geo_bypass": True,
    "socket_timeout": REQUEST_TIMEOUT,
    "http_headers": {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    },
}


def extract_info(url: str, download: bool = False) -> Dict[str, Any]:
    """
    Instagram ভিডিও/রিল/IGTV থেকে মেটাডাটা আনে (বা চাইলে ডাউনলোডও করতে পারে)।
    """
    opts = YDL_OPTS_BASE.copy()
    opts["skip_download"] = not download

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=download)
        return info


def pick_best_formats(info: Dict[str, Any]) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    mp4 format গুলার মধ্যে সবচেয়ে ভালোটা (best), fallback আর thumbnail বের করে।
    """
    formats: List[Dict[str, Any]] = info.get("formats", [])

    def is_mp4(f: Dict[str, Any]) -> bool:
        ext = f.get("ext")
        vcodec = f.get("vcodec")
        return ext == "mp4" and (vcodec and vcodec != "none")

    mp4s = [f for f in formats if is_mp4(f) and f.get("url")]

    # Sort by resolution + bitrate
    mp4s.sort(key=lambda f: (f.get("height") or 0, f.get("tbr") or 0), reverse=True)

    best = mp4s[0] if mp4s else None
    fallback = mp4s[-1] if len(mp4s) > 1 else None

    # Thumbnail বের করা
    thumbnails = info.get("thumbnails") or []
    thumb = None
    if thumbnails:
        thumb = sorted(
            thumbnails,
            key=lambda t: (t.get("height") or 0, t.get("width") or 0)
        )[-1]

    return {"best": best, "fallback": fallback, "thumbnail": thumb}
