from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def ok(data=None, status: int = 200) -> Response:
    return Response({"success": True, "data": data}, status=status)


def fail(code: str, message: str, status: int = 400) -> Response:
    return Response(
        {"success": False, "error": {"code": code, "message": message}},
        status=status,
    )


def envelope_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data
    code = "error"
    message = "request failed"

    if isinstance(detail, dict):
        if "code" in detail and "message" in detail:
            code = str(detail["code"])
            message = str(detail["message"])
        elif "detail" in detail:
            message = str(detail["detail"])
            if response.status_code == 401:
                code = "unauthorized"
            elif response.status_code == 403:
                code = "forbidden"
            elif response.status_code == 404:
                code = "not_found"
        else:
            # Validation errors
            code = "validation_error"
            message = "; ".join(
                f"{k}: {v}" for k, v in detail.items() if k != "success"
            )
    elif isinstance(detail, list) and detail:
        message = str(detail[0])
    else:
        message = str(detail)

    if response.status_code == 401 and code == "error":
        code = "unauthorized"
    if response.status_code == 403 and code == "error":
        code = "forbidden"

    response.data = {"success": False, "error": {"code": code, "message": message}}
    return response
