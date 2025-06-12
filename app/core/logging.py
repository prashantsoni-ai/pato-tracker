import logging
from .config import settings

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log") if not settings.debug else logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()
