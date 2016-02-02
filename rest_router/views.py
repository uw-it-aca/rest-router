from django.shortcuts import render
from django.http import HttpResponse
from rest_router.util import get_service_name, has_access_to_service
from rest_router.util import get_response


# Create your views here.
def proxy(request, service, url):
    client_service = get_service_name(request)
    if not client_service:
        return access_denied("No client identification provided")

    if not has_access_to_service(client_service, service):
        return access_denied("Your app doesn't have access to %s" % service)

    method = request.method
    body = request.body

    url += "?%s" % request.META["QUERY_STRING"]

    headers = {}
    for header in request.META:
        headers[header] = request.META[header]

    try:
        response = get_response(client_service, service, method, url, body,
                                headers)
    except Exception as ex:
        print "E: ", ex
        raise

    return response


def access_denied(msg=""):
    response = HttpResponse(msg)
    response["Content-type"] = "text/plain"
    response.status_code = 403
    return response
