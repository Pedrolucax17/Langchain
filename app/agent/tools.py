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

UUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")


def _normalize_phone(s: str) -> str:
    return re.sub(r"\D+", "", s or "")


def _is_uuid(s: str) -> bool:
    return bool(s) and bool(UUID_RE.match(s))

def _resolve_lead_id_by_ref(cur, ref: str) -> Tuple[Optional[str], List[Dict[str, Any]]]:
  """
  Resolve um lead a partir de uma referência natual (uuid/email/telefone/nome+empresa).
  Retorna (lead_id_ou_none, matches_para_desambiguação).
  """
  
  if not ref:
    return None, []
  ref = ref.strip()
  if _is_uuid(ref):
    cur.execute("SELECT id,nome,email,empresa FROM public.leads WHERE id = %s", (ref,))
    row = cur.fetchone()
    return (row[0], []) if row else (None, [])
  
  if "@" in ref:
    cur.execute(
      "SELECT id,nome,email,empresa FROM public.leads WHERE lower(email)=lower(%s)", (ref,)
    )
    row = cur.fetchone()
    return (row[0], []) if row else (None, [])
  digits = _normalize_phone(ref)
  if len(digits) >= 8:
    cur.execute(
      "SELECT id,nome,email,empresa FROM public.leads WHERE regexp_replace(telefone, '[^0-9]', '', 'g')=%s", (digits, )
    )
    row = cur.fetchone()
    return (row[0], []) if row else (None, [])
  
  # Nome/Empresa
  like = f"%{ref.lower}%"
  cur.execute(
    """
    SELECT id,nome,email,empresa
    FROM public.leads
    WHERE lower(nome) like %s or lower(empresa) like %s
    ORDER BY criado_em desc
    LIMIT 5
    """,
    (like, like)
  )
  rows = cur.fetchall() or []
  if len(rows) == 1:
    return rows[0][0], []
  return None, [
    {"lead_id": r[0], "nome": r[1], "email": r[2], "empresa": r[3]} for r in rows
  ]
  
@tool
def criar_lead(
  nome: str,
    email: Optional[str] = None,
    telefone: Optional[str] = None,
    empresa: Optional[str] = None,
    origem: Optional[str] = None,
    status_codigo: str = "novo",
) -> Dict[str, Any]:
  """Cria um lead. Campos: nome (obrigatório), email, telefone, empresa, origem. 
  Usa status_codigo (default: novo)."""
  if not nome:
    return {"error": {"message": "Campo 'nome' é obrigatório"}}
  with _conn() as conn:
    with conn.cursor() as cur:
      cur.execute("SELECT 1 FROM public.status_lead WHERE codigo=%s", (status_codigo,))
      if not cur.fetchone():
        return {"error": {"status_codigo inválido: {status_codigo}"}}
      #Checar unicidade email/telefone
      if email:
        cur.execute(
          "SELECT 1 FROM public.leads WHERE lower(email)=lower(%s)", (email,)
        )
        if cur.fetchone():
          {"error": {"message": "Já existe lead com este email."}}
      if telefone:
        cur.execute(
          "SELECT 1 FROM public.leads WHERE regexp_replace(telefone,'[^0-9]','','g')=%s",
          (_normalize_phone(telefone),)
        )
        if cur.fetchone():
          {"error": {"message": "Já existe lead com este telefone."}}
      cur.execute(
        """
        INSERT INTO public.leads (nome, email, telefone, empresa, origem, status_codigo)
        VALUES (%s, %s, %s, %s, %s, %s)
        returning id
        """,
        (nome, email, telefone, empresa, origem, status_codigo)
      )
      lead_id = cur.fetchone()[0]
  return {"message": "Lead criado", "data": {"lead_id": lead_id, "nome": nome, "email": email, "empresa": empresa}}