from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    detail = response.data
    message = "Request failed"
    errors = detail

    if isinstance(detail, dict):
        if "detail" in detail and len(detail) == 1:
            message = str(detail["detail"])
            errors = None
    elif isinstance(detail, list) and len(detail) == 1:
        message = str(detail[0])
        errors = None

    response.data = {"success": False, "message": message, "errors": errors}
    return response
