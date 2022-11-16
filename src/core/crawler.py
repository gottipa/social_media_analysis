"""Data model for source core modules
"""
#
import time
from core.logger import logger as log
from model.base import BaseModel
from model.crawler import Crawler as CrawlerModel


class Crawler(BaseModel):
    """Crawler class

    :param _type_ Source: _description_
    :raises ValueError: _description_
    """

    def __init__(self, **kwargs) -> None:
        model = CrawlerModel(**kwargs)
        self.mode = model.mode
        self.entity = model.entity
        self.max_limits = model.max_limits
        self.is_stopped = model.is_stopped

    def stop(self):
        """Stop crawler"""
        log.debug(f"Stopping {self.__class__}")
        self.is_stopped = True
        time.sleep(3)
        log.info(f"Stopped {self.__class__}")

    def run(self):
        """Run crawler

        :yield _type_: _description_
        """
        base_runner = self.mode.value
        entities = iter(self.entity)
        log.info(f"Running crawler for {self.entity}")
        while not self.is_stopped:
            try:
                entity = next(entities)
                scraper = base_runner(entity)
                count = 0
                for item in scraper.get_items():
                    if count > self.max_limits:
                        break
                    count += 1
                    yield (item, entity)
            except StopIteration:
                self.is_stopped = True
                break
