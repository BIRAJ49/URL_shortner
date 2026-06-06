# Django URL Shortener

This project is a URL shortener web application built with Django.

The project includes user authentication so users can register, log in, and log out. Only logged-in users can create and manage short URLs.

Long URLs are saved with a short key. The app supports automatic short key generation using SHA-256, and users can also choose a custom short key if it is available.

Each user can view a list of their own short URLs, edit existing URLs, or delete them. Every short URL stores its creation date, optional expiration time, and click count.

When a short URL is opened, the app redirects to the original long URL and updates the click count. Expired URLs no longer redirect.

The project also includes QR code generation for short URLs and basic tests for the main features.
