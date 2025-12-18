def success_response(message, data=None):
    return {
        "status": "success",
        "message": message,
        "data": data or {}
    }

def failure_response(message, errors=None):
    return {
        "status": "failure",
        "message": message,
        "errors": errors
    }
