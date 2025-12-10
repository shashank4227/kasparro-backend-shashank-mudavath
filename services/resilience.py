import time
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Simple token bucket style rate limiter.
    Ensures that we don't exceed `calls_per_second`.
    """
    def __init__(self, calls_per_second: float):
        self.interval = 1.0 / calls_per_second
        self.last_call_time = 0.0

    def wait_for_token(self):
        """
        Blocks until enough time has passed since the last call.
        """
        current_time = time.time()
        elapsed = current_time - self.last_call_time
        
        if elapsed < self.interval:
            sleep_time = self.interval - elapsed
            logger.info(f"Rate limit hit. Sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_call_time = time.time()

# Standard retry configuration for external APIs
# Retries on Network Errors (ConnectionError, Timeout) and 5xx Server Errors.
# Does NOT retry on 4xx Client Errors (except maybe 429 if we wanted to be fancy, but 429 is usually handled by backoff + rate limiting).
def validation_retry():
    return retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((
            requests.exceptions.ConnectionError, 
            requests.exceptions.Timeout,
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.HTTPError 
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
