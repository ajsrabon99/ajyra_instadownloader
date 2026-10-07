# AJYRA InstaDownloader

A simple, fast web app for downloading **Instagram videos, Reels and IGTV** by pasting a link. Built with **Django** and powered by **yt-dlp**.

Paste a URL, preview the video right in the browser, and download it as an MP4.

---

## Features

- **Paste & fetch**: enter an Instagram video / Reel / IGTV URL and get the title, uploader, duration and thumbnail.
- **In-browser preview**: stream the video through a built-in proxy before downloading.
- **Two download methods**
  - *Streaming proxy*: streams the MP4 straight to the user.
  - *yt-dlp download*: downloads to a temp file on the server, serves it, then cleans it up automatically.
- **About & Contact pages**: contact form submissions are saved to the database.
- **Django Admin**: view and search contact messages at `/admin/`.
- **Deploy-ready**: includes a `Procfile` for Gunicorn-based platforms (Render, Railway, Heroku, etc.).

---

## Tech Stack

| Layer      | Technology                                  |
| ---------- | ------------------------------------------- |
| Backend    | Python 3.11, Django 5.1                     |
| Downloader | [yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| HTTP       | requests                                    |
| Server     | Gunicorn                                    |
| Database   | SQLite (default)                            |
| Frontend   | Django templates, HTML/CSS                  |

---

## Project Structure

```
ajyra_instadownloader-main/
├── ajyra_instadownloader/     # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py / asgi.py
├── instadw/                   # Main app
│   ├── templates/instadw/     # base, home, about, contact
│   ├── forms.py               # VideoForm (URL input)
│   ├── models.py              # ContactMessage
│   ├── views.py               # home, proxies, yt-dlp download, about, contact
│   ├── utils.py               # yt-dlp helpers (extract info, pick best format)
│   ├── urls.py
│   └── admin.py
├── Procfile                   # web: gunicorn ajyra_instadownloader.wsgi
├── requirements.txt
├── manage.py
└── db.sqlite3
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- `pip`
- (Recommended) [FFmpeg](https://ffmpeg.org/download.html) installed and on your `PATH`. yt-dlp uses it to merge video/audio streams when needed.

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd ajyra_instadownloader-main

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. (Optional) Create an admin user
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## Usage

1. Open the home page.
2. Paste a public Instagram video, Reel or IGTV link.
3. Click the fetch/download button.
4. Preview the video, then download it.

---

## Routes

| URL                                          | Description                                              |
| -------------------------------------------- | -------------------------------------------------------- |
| `/`                                          | Home page and URL form                                   |
| `/play_proxy/?url=<video_url>`               | Streams a video for in-browser playback                  |
| `/download_proxy/?url=<video_url>&title=...` | Streams a video as a downloadable `.mp4`                 |
| `/download_via_ytdlp/?video_url=<ig_url>`    | Downloads via yt-dlp and returns the file (`&play=true` to play inline) |
| `/about/`                                    | About page                                               |
| `/contact/`                                  | Contact form (saved to database)                         |
| `/admin/`                                    | Django admin                                             |

---

## Configuration

Most settings live in `ajyra_instadownloader/settings.py`.

**Contact form email (optional)**: configure SMTP in `settings.py`:

```python
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email@gmail.com"
EMAIL_HOST_PASSWORD = "your-gmail-app-password"   # use a Gmail App Password
```

**Request timeout**: set the `REQUESTS_TIMEOUT` environment variable (default `25` seconds) to change the yt-dlp socket timeout.

---

## Deployment

The project ships with a `Procfile`:

```
web: gunicorn ajyra_instadownloader.wsgi
```

It can be deployed to any platform that supports Python and Gunicorn (Render, Railway, Heroku, a VPS, etc.).

**Before going to production, please:**

1. **Move secrets out of the code.** Load `SECRET_KEY` and email credentials from environment variables (`python-decouple` and `python-dotenv` are already in `requirements.txt`), and never commit real credentials.
2. **Set `DEBUG = False`.**
3. **Restrict `ALLOWED_HOSTS`** to your real domain(s) instead of `['*']`.
4. **Configure static files.** Create a `static/` folder (referenced by `STATICFILES_DIRS`), run `python manage.py collectstatic`, and enable WhiteNoise (already installed) in `MIDDLEWARE` if you serve static files from Gunicorn.
5. **Use a persistent database** (e.g. PostgreSQL via `dj-database-url` + `psycopg2-binary`, both already in `requirements.txt`). SQLite data is lost on ephemeral hosts.
6. **Restrict the proxy endpoints.** `play_proxy` and `download_proxy` fetch whatever URL they are given, so validate that it points to an expected Instagram/CDN host and add rate limiting before exposing them publicly.

---

## Notes

- Only **publicly accessible** content can be fetched. Private accounts are not supported.
- Instagram changes frequently. If downloads stop working, update yt-dlp first:
  ```bash
  pip install -U yt-dlp
  ```
- `requirements.txt` contains several packages the app does not currently use (e.g. Flask, Firebase, Stripe). They can be trimmed to speed up installs.

---

## Disclaimer

This tool is intended for **personal use** with content you own or have permission to download. You are responsible for respecting Instagram's Terms of Service, copyright law and the rights of content creators. The authors are not affiliated with Instagram or Meta.

---

## Contributing

Issues and pull requests are welcome. For larger changes, please open an issue first to discuss what you would like to change.

---

## License

Add a license of your choice (for example MIT) in a `LICENSE` file.
