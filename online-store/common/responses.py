from rest_framework import status as drf_status
from rest_framework.response import Response


class APIResponse:
    @staticmethod
    def success(data=None, message="OK", status=drf_status.HTTP_200_OK):
        return Response(
            {"success": True, "message": message, "data": data}, status=status
        )

    @staticmethod
    def created(data=None, message="Created"):
        return APIResponse.success(data, message, drf_status.HTTP_201_CREATED)

    @staticmethod
    def no_content(message="No Content"):
        return Response(
            {"success": True, "message": message}, status=drf_status.HTTP_204_NO_CONTENT
        )

    @staticmethod
    def error(message="Error", errors=None, status=drf_status.HTTP_400_BAD_REQUEST):
        return Response(
            {"success": False, "message": message, "errors": errors}, status=status
        )
