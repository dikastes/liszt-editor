class HTMXPreloadCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method == "GET" and request.headers.get("Hx-Preloaded") == "true":
            response["Cache-Control"] = "public, max-age=60"
        return response
