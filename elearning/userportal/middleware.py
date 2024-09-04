# Django Middleware to handle 405 Method Not Allowed Error
# This middleware intercepts responses to manage HTTP 405 errors by rendering a custom template.
# Inspired by and adapted from a Stack Overflow solution at:
# https://stackoverflow.com/a/71455109


from django.http import HttpResponse
from django.template import loader


class HttpResponseNotAllowedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # If the response status code is 405, render a custom template
        if response.status_code == 405:
            print("405 error")
            context = {}
            template = loader.get_template("405.html")
            return HttpResponse(template.render(context, request), status=405)

        return response
