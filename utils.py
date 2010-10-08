from django.http import HttpResponse as response
from django.http import HttpResponseNotAllowed
from django.shortcuts import render_to_response
from django.template import RequestContext

class ViewClass:
    def __call__(self, request, *args, **kwargs):
        self.request = request
        self.methods = [method for method in dir(self)\
            if callable(getattr(self, method))]

        if request.method in self.methods:
            view = getattr(self, request.method)
            return view(*args, **kwargs)
        else:
            return HttpResponseNotAllowed(self.methods)

    def context_response(self, *args, **kwargs):
        kwargs['context_instance'] = RequestContext(self.request)
        return render_to_response(*args, **kwargs)