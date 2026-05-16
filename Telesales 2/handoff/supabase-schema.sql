-- Telesales — Schema Supabase completo
-- Esegui nel SQL editor di Supabase

-- Enable UUID
create extension if not exists "uuid-ossp";

-- ============ AUTH ============
-- Supabase gestisce auth.users automaticamente

-- ============ PROFILES ============
create table public.profiles (
  id uuid references auth.users primary key,
  nome text,
  cognome text,
  azienda text,
  ruolo text,
  avatar_url text,
  piano text default 'starter', -- starter | growth | enterprise
  created_at timestamptz default now()
);

alter table profiles enable row level security;
create policy "Users can view own profile" on profiles for select using (auth.uid() = id);
create policy "Users can update own profile" on profiles for update using (auth.uid() = id);

-- ============ CONTACTS (CRM WAR ROOM) ============
create table public.contacts (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  cognome text,
  email text,
  tel text,
  azienda text,
  ruolo text,
  linkedin_url text,
  stato text default 'cold' check (stato in ('hot','warm','cold','won','lost')),
  score int default 0 check (score between 0 and 100),
  note text,
  tags text[],
  owner_id uuid references auth.users,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table contacts enable row level security;
create policy "Users see own contacts" on contacts for all using (auth.uid() = owner_id);

-- ============ CALLS ============
create table public.calls (
  id uuid primary key default gen_random_uuid(),
  contact_id uuid references contacts,
  agent_name text default 'Marco',
  direction text default 'outbound' check (direction in ('outbound','inbound')),
  duration_sec int,
  status text check (status in ('completed','missed','failed','live')),
  transcript text,
  sentiment float check (sentiment between -1 and 1),
  recording_url text,
  vapi_call_id text,
  owner_id uuid references auth.users,
  created_at timestamptz default now()
);

alter table calls enable row level security;
create policy "Users see own calls" on calls for all using (auth.uid() = owner_id);

-- ============ PIPELINE ============
create table public.opportunities (
  id uuid primary key default gen_random_uuid(),
  contact_id uuid references contacts,
  titolo text not null,
  valore_eur int,
  stage text default 'nuovo' check (stage in ('nuovo','contattato','qualificato','proposta','chiuso_vinto','chiuso_perso')),
  probabilita int default 50 check (probabilita between 0 and 100),
  data_chiusura date,
  note text,
  owner_id uuid references auth.users,
  created_at timestamptz default now()
);

alter table opportunities enable row level security;
create policy "Users see own opps" on opportunities for all using (auth.uid() = owner_id);

-- ============ OUTREACH SEQUENCES ============
create table public.sequences (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  segmento text,
  canali text[] default '{email}',
  tono text default 'diretto',
  step_count int default 7,
  status text default 'draft' check (status in ('draft','active','paused','completed')),
  contacts_count int default 0,
  reply_rate float,
  owner_id uuid references auth.users,
  created_at timestamptz default now()
);

-- ============ SCRAPED CONTACTS (Lead Founder AI) ============
create table public.scraped_contacts (
  id uuid primary key default gen_random_uuid(),
  nome text,
  azienda text,
  ruolo text,
  email text,
  tel text,
  linkedin_url text,
  geo text,
  source text, -- linkedin | crunchbase | registro_imprese | apify
  tags text[],
  enriched bool default false,
  verified bool default false,
  imported_to_crm bool default false,
  created_at timestamptz default now()
);

-- Realtime per lo stream live
alter publication supabase_realtime add table scraped_contacts;

-- ============ HR / TALENTIA ============
create table public.hr_positions (
  id uuid primary key default gen_random_uuid(),
  titolo text not null,
  sede text,
  contratto text,
  ral_min int,
  ral_max int,
  must_have text,
  shortlist_size int default 5,
  status text default 'aperta' check (status in ('aperta','pausa','chiusa')),
  owner_id uuid references auth.users,
  created_at timestamptz default now()
);

create table public.hr_candidates (
  id uuid primary key default gen_random_uuid(),
  position_id uuid references hr_positions,
  nome text not null,
  cognome text,
  email text,
  linkedin_url text,
  ruolo_attuale text,
  azienda_attuale text,
  anni_exp int,
  fit_score int check (fit_score between 0 and 100),
  call_duration_sec int,
  transcript text,
  summary text,
  stato text default 'shortlist' check (stato in ('shortlist','colloquio','rifiutato','offerta','accettato')),
  disponibilita text,
  created_at timestamptz default now()
);

-- ============ BANDI / PA WINNER ============
create table public.bandi (
  id uuid primary key default gen_random_uuid(),
  titolo text not null,
  ente text,
  tipo text check (tipo in ('nazionale','europeo','regionale','comunale')),
  importo_max_eur int,
  scadenza date,
  stato text default 'attivo' check (stato in ('attivo','chiuso','prossimo')),
  fit_score int check (fit_score between 0 and 100),
  match bool default false,
  url text,
  note text,
  tags text[],
  created_at timestamptz default now()
);

-- ============ EVENTS / EVENTIA ============
create table public.events (
  id uuid primary key default gen_random_uuid(),
  titolo text not null,
  formato text check (formato in ('in_person','webinar','workshop','retreat')),
  data date,
  luogo text,
  capienza int,
  iscritti int default 0,
  sponsor_count int default 0,
  sponsor_revenue_eur int default 0,
  status text default 'pianificato' check (status in ('pianificato','aperto','chiuso','completato')),
  owner_id uuid references auth.users,
  created_at timestamptz default now()
);

-- ============ PRODUCTS / PRODUCT MAKER AI ============
create table public.digital_products (
  id uuid primary key default gen_random_uuid(),
  titolo text not null,
  tipo text check (tipo in ('corso','playbook','template','membership','ebook','masterclass')),
  prezzo_eur int,
  venduti int default 0,
  revenue_eur int default 0,
  conv_rate float,
  status text default 'live' check (status in ('bozza','live','pausa','archiviato')),
  checkout_url text,
  owner_id uuid references auth.users,
  created_at timestamptz default now()
);

-- ============ BOOKING DEMO ============
create table public.demo_bookings (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  cognome text,
  email text not null,
  tel text,
  azienda text,
  messaggio text,
  status text default 'nuovo' check (status in ('nuovo','confermato','completato','annullato')),
  source text default 'landing',
  created_at timestamptz default now()
);

-- ============ INDEXES ============
create index on contacts(owner_id, stato);
create index on calls(owner_id, created_at desc);
create index on opportunities(owner_id, stage);
create index on scraped_contacts(created_at desc);
create index on bandi(scadenza, match);
create index on hr_candidates(position_id, fit_score desc);

-- ============ TRIGGER updated_at ============
create or replace function update_updated_at()
returns trigger as $$
begin new.updated_at = now(); return new; end;
$$ language plpgsql;

create trigger contacts_updated_at before update on contacts
  for each row execute function update_updated_at();

-- Done ✅
