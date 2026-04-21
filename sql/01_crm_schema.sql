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

-- Tabela principal de leads
CREATE TABLE if NOT EXISTS public.leads(
  id uuid PRIMARY KEY default gen_random_uuid(),
  nome TEXT NOT NULL,
  email TEXT UNIQUE,
  telefone TEXT,
  empresa TEXT,
  origem TEXT,
  qualificado boolean NOT NULL default false,
  status_codigo TEXT NOT NULL REFERENCES public.status_lead(codigo) default 'novo',
  ultimo_contato_em timestamptz,
  proxima_acao_em timestamptz,
  criacao_em timestamptz NOT NULL default now(),
  atualizado_em timestamptz NOT NULL now()
);

-- Comentários (documentação)
comment on table public.leads is 'Entidade principal de leads (potenciais clientes).';
comment on column public.leads.id is 'Identificador único do lead (UUID).';
comment on column public.leads.nome is 'Nome do lead ou contato principal.';
comment on column public.leads.email is 'E-mail do lead (único quando preenchido).';
comment on column public.leads.telefone is 'Telefone do lead (formato livre).';
comment on column public.leads.empresa is 'Empresa do lead.';
comment on column public.leads.origem is 'Origem do lead (campanha, canal etc.).';
comment on column public.leads.qualificado is 'Indica se o lead está qualificado.';
comment on column public.leads.status_codigo is 'Código do status do lead (FK para status_lead.codigo).';
comment on column public.leads.ultimo_contato_em is 'Data/hora do último contato.';
comment on column public.leads.proxima_acao_em is 'Data/hora da próxima ação planejada.';
comment on column public.leads.criado_em is 'Timestamp de criação.';
comment on column public.leads.atualizado_em is 'Timestamp da última atualização.';