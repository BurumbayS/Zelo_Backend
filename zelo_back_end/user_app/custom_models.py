from django.http import JsonResponse

class ErrorResponse:
    def response(text):
        return JsonResponse({"code": 1, "error": text})
