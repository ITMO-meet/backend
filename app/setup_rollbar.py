import rollbar
import os
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

def init_rollbar():
    rollbar.init(
        access_token=os.getenv("ROLLBAR_TOKEN"),
        environment="production"
    )
    rollbar.report_message("Rollbar initialized successfully", "info")

def rollbar_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if os.getenv("TEST_ENV") != "true":
                rollbar.report_exc_info()      
            raise e
    return wrapper

# def main():
#     raise rollbar.ApiError("No token =/")
#     # rollbar.init('post_server_item_token', 'testenv')  # токен доступа, среда
#     # rollbar.report_message('Test message from backend', 'info')


# if __name__ == "__main__":  # pragma: no cover
#     main()
