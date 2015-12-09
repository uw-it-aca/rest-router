from django.conf import settings
import json
import urllib3
from urlparse import urlparse
from django.http import HttpResponse
import six
if six.PY2:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin


def get_service_name(request):
    return request.META.get("SSL_CLIENT_S_DN_CN", "")


def has_access_to_service(client, service):
    data = config_data()

    try:
        return data["clients"][client]["services"][service]
    except KeyError:
        return False

    return False


def config_data():
    config_path = settings.R2_ACCESS_FILE
    f = open(config_path)
    data = f.read()
    values = json.loads(data)
    return values


def get_response(client_service, service, method, url, body, headers):
    data = config_data()

    if not has_access_to_service(client_service, service):
        raise Exception("Access Denied")

    cert = data["clients"][client_service].get("cert_path", None)
    key = data["clients"][client_service].get("key_path", None)

    timeout = get_timeout(client_service, service)

    service_base = data["services"][service]["url"]

    kwargs = {
        "timeout": timeout,
        "maxsize": 1,
        "block": True,
        }

    if urlparse(url).scheme == "https":
        if key is not None and cert is not None:
            kwargs["key_file"] = key
            kwargs["cert_file"] = cert

        kwargs["ssl_version"] = ssl.PROTOCOL_TLSv1
        kwargs["cert_reqs"] = "CERT_REQUIRED"
        kwargs["ca_certs"] = getattr(settings, "REST_ROUTER_CA_BUNDLE",
                                     "/etc/ssl/certs/ca-bundle.crt")

    # This is the full name so it can be overridden in the tests.
    full_url = urljoin(service_base, url)
    conn = urllib3.connection_from_url(full_url, **kwargs)

    service_response = conn.urlopen(method, full_url, body=body,
                                    headers=headers,
                                    timeout=timeout)

    response = HttpResponse(service_response.content)
    response.status_code = service_response.status_code

    return response


def get_timeout(client_service, service):
    data = config_data()
    timeout = data["services"][service].get("timeout", 15)

    try:
        timeout = data["clients"][client_service]["timeout_override"][service]
    except KeyError:
        pass

    return timeout
