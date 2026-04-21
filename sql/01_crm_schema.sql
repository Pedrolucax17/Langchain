create extention if not exists "pgcrypto";

-- Tabela de lookup para status de leads
CREATE TABLE if not exists public.status_lead(
  codigo text PRIMARY KEY,
  rotulo text NOT NULL,
  criado_em timestamptz NOT NULL default now()
);

-- Comentários (Documentação)
comment on table public.status_lead is 'Lookup de status de lead(tabela de referência).';
comment on table public.status_lead.codigo is 'Código do status (PK), ex: novo, qualificado.';
comment on table public.status_lead.rotulo is 'Rótulo amigável do status.';
comment on table public.status_lead.criado_em is 'Timestamp de criação do registro';
