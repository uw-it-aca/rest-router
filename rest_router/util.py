from django.conf import settings


def get_service_name(request):
    return request.META.get("SSL_CLIENT_S_DN_CN", "")


def has_access_to_service(client, service):
    return False
