from redis import Redis
from rq import Worker
from gpt_researcher.scraper.scraper import Scraper

# https://python-rq.org/docs/workers/#performance-notes
w = Worker(['default'], connection=Redis())
w.work()
