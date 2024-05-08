from redis import Redis
from rq import Worker
import re
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from gpt_researcher.scraper.scraper import Scraper

# https://python-rq.org/docs/workers/#performance-notes
w = Worker(['default'], connection=Redis())
w.work()
