import os
import django
from django.urls import get_resolver, URLPattern, URLResolver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def show_urls(patterns, prefix=""):
    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            show_urls(pattern.url_patterns, prefix + pattern.pattern.regex.pattern.lstrip('^'))
        elif isinstance(pattern, URLPattern):
            print(f"{prefix}{pattern.pattern.regex.pattern.lstrip('^')}")

print("Registered URL patterns:")
show_urls(get_resolver().url_patterns)
