import email as emaillib
import json
import smtplib
from textwrap import dedent

import prometheus_client
from blacksmith import SyncConsulDiscovery
from django.http import HttpRequest, HttpResponse, JsonResponse
from prometheus_client.multiprocess import MultiProcessCollector

from dj_blacksmith import SyncDjBlacksmithClient
from notif.resources.user import User

smtp_sd = SyncConsulDiscovery(unversioned_service_url_fmt="{address} {port}")


def send_email(user: User, message: str):
    email_content = dedent(
        f"""\
        Subject: notification
        From: notification@localhost
        To: "{user.firstname} {user.lastname}" <{user.email}>

        {message}
        """
    )
    msg = emaillib.message_from_string(email_content)

    srv = smtp_sd.resolve("smtp", None)
    # XXX Synchronous socket here, OK for the example
    # real code should use aiosmtplib
    s = smtplib.SMTP(srv.address, int(srv.port))
    s.send_message(msg)
    s.quit()


def post_notification(request: HttpRequest) -> HttpResponse:
    dj_cli = SyncDjBlacksmithClient(request)
    cli = dj_cli("default")
    api_user = cli("api_user")
    body = json.loads(request.body.decode("utf-8"))
    user: User = (api_user.users.get({"username": body["username"]})).response
    send_email(user, body["message"])
    return JsonResponse({"detail": f"{user.email} accepted"}, status=202)


def get_metrics(request: HttpRequest) -> HttpResponse:
    registry = prometheus_client.CollectorRegistry()
    MultiProcessCollector(registry)
    metrics_page = prometheus_client.generate_latest(registry)
    return HttpResponse(
        metrics_page, content_type=prometheus_client.CONTENT_TYPE_LATEST
    )
