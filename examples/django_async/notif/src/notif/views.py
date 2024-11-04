import email as emaillib
import json
import smtplib
from textwrap import dedent

import prometheus_client
from blacksmith import AsyncConsulDiscovery
from django.http import HttpRequest, HttpResponse, JsonResponse

from dj_blacksmith import AsyncDjBlacksmithClient
from notif.resources.user import User

smtp_sd = AsyncConsulDiscovery(unversioned_service_url_fmt="{address} {port}")


async def send_email(user: User, message: str):
    email_content = dedent(
        f"""\
        Subject: notification
        From: notification@localhost
        To: "{user.firstname} {user.lastname}" <{user.email}>

        {message}
        """
    )
    msg = emaillib.message_from_string(email_content)

    srv = await smtp_sd.resolve("smtp", None)
    # XXX Synchronous socket here, OK for the example
    # real code should use aiosmtplib
    s = smtplib.SMTP(srv.address, int(srv.port))
    s.send_message(msg)
    s.quit()


async def post_notification(request: HttpRequest) -> HttpResponse:
    dj_cli = AsyncDjBlacksmithClient(request)
    cli = await dj_cli("default")
    api_user = await cli("api_user")
    body = json.loads(request.body.decode("utf-8"))
    user: User = (await api_user.users.get({"username": body["username"]})).response
    await send_email(user, body["message"])
    return JsonResponse({"detail": f"{user.email} accepted"}, status=202)


async def get_metrics(request: HttpRequest) -> HttpResponse:
    registry = prometheus_client.REGISTRY
    metrics_page = prometheus_client.generate_latest(registry)
    return HttpResponse(
        metrics_page, content_type=prometheus_client.CONTENT_TYPE_LATEST
    )
