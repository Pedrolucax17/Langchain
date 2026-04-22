import os 
import re 
from typing import Any, Dict, List, Optional, Tuple

import psycopg
from langchain_core.tools import tool

def _db_url() -> str:
  user = os.getenv("DB_USER")
  pwd = os.getenv("DB_PASSWORD")
  host = os.getenv("DB_HOST")
  port = os.getenv("DB_PORT")
  name = os.getenv("DB_NAME")
  if not all([user, pwd, host, name]):
    raise RuntimeError("Defina DB_USER, DB_PASSWORD, DB_HOST, DB_NAME e opcionalmente DB_PORT/DB_SSLMODE ")
  sslmode = os.getenv("DB_SSLMODE", "require")
  return f"postgresql://{user}:{pwd}@{host}:{port}/{name}?sslmode={sslmode}"

def _conn():
  return psycopg.connect(_db_url())