from django.shortcuts import render
from django.http import HttpResponse
from rest_router.util import get_service_name, has_access_to_service


# Create your views here.
def proxy(request, service, url):
    client_service = get_service_name(request)

    if not has_access_to_service(client_service, service):
        return access_denied("Your app doesn't have access to %s" % service)

    return HttpResponse("OK!")


def access_denied(msg=""):
    response = HttpResponse(msg)
    response["Content-type"] = "text/plain"
    response.status_code = 403
    return response
