from django.utils.deprecation import MiddlewareMixin

class CustomMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Add custom processing here
        pass

    def process_response(self, request, response):
        # Add custom processing here
        return response