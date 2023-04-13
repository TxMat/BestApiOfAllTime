def error_handler(ctx, error_code, error_message):
    error = {
        "errors": {
            ctx: {
                "code": error_code,
                "name": error_message
            }
        }
    }
    return error
