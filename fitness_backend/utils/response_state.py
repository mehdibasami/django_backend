from rest_framework.response import Response
from rest_framework import status


class SuccessResponse(Response):
    def __init__(self, data=None, message="success", status=status.HTTP_200_OK, dev_message='', **kwargs):
        response_data = {
            "message": message,
            "data": data,
        }
        super().__init__(response_data, status=status, **kwargs)


class SuccessResponse201(SuccessResponse):
    def __init__(self, data=None, message="success", status=status.HTTP_201_CREATED, **kwargs):
        super().__init__(data=data, message=message, status=status, **kwargs)


class BadRequestResponse(Response):
    def __init__(self, data=None, errors=None, message="Failed", status=status.HTTP_400_BAD_REQUEST, **kwargs):
        response_data = {
            "message": message,
            "errors": errors,
            "data": data,
        }
        super().__init__(response_data, status=status, **kwargs)


class NotFoundResponse(Response):
    def __init__(self, data=None, status=status.HTTP_404_NOT_FOUND, message="Not found 404", **kwargs):
        response_data = {
            "message": message,
            "data": data,

        }
        super().__init__(response_data, status=status, **kwargs)


class ForbiddenResponse(Response):
    def __init__(self, data=None, status=status.HTTP_403_FORBIDDEN, message="Forbidden 403", **kwargs):

        response_data = {
            "message": message,
            "data": data,

        }
        super().__init__(response_data, status=status, **kwargs)


class ServerErrorResponse(Response):
    def __init__(self, message="Something Went Wrong, Please Try Again Later", data=None, status=status.HTTP_500_INTERNAL_SERVER_ERROR, errors=None, **kwargs):
        response_data = {
            "message": message,
            "errors": errors,
            "data": data,
        }
        super().__init__(response_data, status=status, **kwargs)


class AuthErrorResponse(Response):
    def __init__(self, message='', data=None, status=status.HTTP_401_UNAUTHORIZED, **kwargs):
        response_data = {
            "message": message,
            "data": data,
        }
        super().__init__(response_data, status=status, **kwargs)
