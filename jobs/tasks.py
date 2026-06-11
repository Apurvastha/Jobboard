import logging
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def debug_task(self):
    """Simple task to verify celery is working."""
    logger.info(f'Request: {self.request!r}')
    return 'Celery is working!'

@shared_task(bind=True, max_retries=3)
def add(self,x,y):
    """Test task - adds two numbers."""
    logger.info(f'Adding {x} + {y}')
    return x + y