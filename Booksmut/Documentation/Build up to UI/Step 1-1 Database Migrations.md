# Step 1-1: Database Migrations

**Purpose:** Create all the database tables that ReelForge needs to function. Each table
stores a specific type of data — books, campaigns, licenses, etc.

You'll run these one at a time in the Supabase SQL Editor. Each block is a separate step.
If one fails, stop and fix it before moving to the next — each table builds on the previous.

**Time:** ~20 minutes

---

## How to Use the SQL Editor

1. Go to your Supabase project dashboard
2. In the left sidebar, click **SQL Editor**
3. Click **New query**
4. Paste the SQL block for the current step
5. Click **Run** (or press Ctrl+Enter)
6. Confirm it says "Success" before moving to the next block
7. Click **New query** again for each new block

---

## Migration 01 — Enable UUID Extension

Supabase uses UUIDs (unique IDs) for all records. This enables that feature.

```sql
create extension if not exists "uuid-ossp";
```

---

## Migration 02 — Tenants

A tenant is one account/user of the system. This table is first because almost every
other table references it.

```sql
create table tenants (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  associate_tag text,
  created_at timestamptz default now()
);
```

---

## Migration 03 — Users and Roles

```sql
create table user_roles (
  id uuid primary key default uuid_generate_v4(),
  tenant_id uuid references tenants(id) on delete cascade,
  user_id uuid not null,
  role text not null check (role in ('OWNER', 'PARTNER', 'VIEWER')),
  created_at timestamptz default now()
);
```

---

## Migration 04 — Books

The core table. Every book the system discovers goes here.

```sql
create table books (
  id uuid primary key default uuid_generate_v4(),
  tenant_id uuid references tenants(id) on delete cascade,

  -- Identifiers
  isbn text,
  google_books_id text,
  hardcover_id text,
  open_library_id text,

  -- Bibliographic data
  title text not null,
  author text not null,
  series_name text,
  series_position int,
  genre text,
  subgenre text,

  -- Cover image
  cover_image_url text,
  cover_image_source text check (cover_image_source in ('PUBLISHER_LICENSED', 'AUTHOR_PROVIDED', 'NONE')),
  cover_cleared_for_use boolean default false,
  use_backdrop_fallback boolean default false,

  -- Content metadata
  description text,
  tropes text[],
  spice_level int check (spice_level between 0 and 5),
  pov_type text,
  setting_primary text,
  setting_mood text,
  aesthetic_tags text[],

  -- Scoring
  score int default 0,
  score_breakdown jsonb,
  force_queued boolean default false,

  -- State
  status text not null default 'DISCOVERED'
    check (status in ('DISCOVERED', 'SCORED', 'ENRICHED', 'ACTIVE', 'REJECTED')),
  cooldown_until timestamptz,

  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

---

## Migration 05 — Book Sources

Records which data source first spotted each book, and how strong the signal was.

```sql
create table book_sources (
  id uuid primary key default uuid_generate_v4(),
  book_id uuid references books(id) on delete cascade,
  source text not null,
  rank int,
  signal_strength int,
  detected_at timestamptz default now()
);
```

---

## Migration 06 — Campaigns

One campaign = one content run against a book (script + video + caption).

```sql
create table campaigns (
  id uuid primary key default uuid_generate_v4(),
  book_id uuid references books(id) on delete cascade,

  -- Campaign configuration
  campaign_type text not null check (campaign_type in (
    'QUICK_TAKE', 'TROPE_BREAKDOWN', 'SPICE_CHECK', 'AUTHOR_SPOTLIGHT',
    'HIDDEN_GEM', 'BOOK_CLUB_PICK', 'SERIES_RANKED', 'TROPE_DEEP_DIVE',
    'AUTHOR_DEEP_DIVE', 'WHY_NOT_OVER_IT', 'ROMANTASY_STARTER_PACK', 'BOOKTOK_DIVIDE'
  )),
  format text not null check (format in ('SINGLE', 'MULTIPART')),
  total_parts int not null default 1,
  created_by text not null check (created_by in ('SYSTEM', 'USER')),
  trigger_reason text,

  -- State
  status text not null default 'CAMPAIGN_DRAFT' check (status in (
    'CAMPAIGN_DRAFT', 'SCRIPTED', 'MODERATION_SCRIPT', 'VOICED', 'COMPOSED',
    'MODERATION_VIDEO', 'MODERATION_FAILED', 'READY', 'SCHEDULED', 'PUBLISHED', 'REJECTED'
  )),

  -- Content
  script_raw jsonb,
  caption text,
  hashtags text[],

  -- Moderation
  moderation_script_status text default 'PENDING'
    check (moderation_script_status in ('PENDING', 'PASSED', 'FAILED', 'SKIPPED')),
  moderation_video_status text default 'PENDING'
    check (moderation_video_status in ('PENDING', 'PASSED', 'FAILED', 'SKIPPED')),
  moderation_script_flags jsonb,
  moderation_video_flags jsonb,
  moderation_override boolean default false,

  -- Error tracking
  retry_count int default 0,
  last_error text,

  -- Timestamps
  scheduled_at timestamptz,
  published_at timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

---

## Migration 07 — Campaign Parts

One row per 30-second reel within a campaign.

```sql
create table campaign_parts (
  id uuid primary key default uuid_generate_v4(),
  campaign_id uuid references campaigns(id) on delete cascade,

  part_number int not null,
  total_parts int not null,

  -- Script content
  hook text,
  body text,
  cta text,
  hook_text text,
  hook_category text,
  caption text,

  -- Generated assets (R2 URLs)
  audio_url text,
  video_url text,
  thumbnail_url text,

  -- Visual configuration
  background_type text check (background_type in ('cover_only', 'setting_video', 'ai_mood_image')),
  music_track_id uuid,

  -- State
  status text not null default 'PENDING' check (status in (
    'PENDING', 'VOICED', 'COMPOSED', 'READY', 'SCHEDULED', 'PUBLISHED',
    'VOICE_FAILED', 'COMPOSE_FAILED'
  )),

  created_at timestamptz default now()
);
```

---

## Migration 08 — Affiliate Links

```sql
create table affiliate_links (
  id uuid primary key default uuid_generate_v4(),
  book_id uuid references books(id) on delete cascade,
  tenant_id uuid references tenants(id) on delete cascade,

  isbn text,
  asin text,
  raw_url text,
  geo_url text,
  link_type text check (link_type in ('AMAZON', 'BOOKSHOP', 'DIRECT')),

  created_at timestamptz default now()
);
```

---

## Migration 09 — Publisher Licenses

Tracks outreach to publishers for cover image licensing.

```sql
create table publisher_licenses (
  id uuid primary key default uuid_generate_v4(),
  tenant_id uuid references tenants(id) on delete cascade,

  publisher_name text not null,
  publisher_domain text,
  contact_name text,
  contact_email text,

  status text not null default 'OUTREACH_PENDING' check (status in (
    'OUTREACH_PENDING', 'IN_DISCUSSION', 'LICENSED', 'DECLINED', 'EXPIRED'
  )),

  license_scope text,
  outreach_date date,
  response_date date,
  license_start date,
  license_expiry date,

  asset_portal_url text,
  asset_portal_login text,

  contact_discovery_method text default 'MANUAL'
    check (contact_discovery_method in ('MANUAL', 'AUTO_CONFIRMED', 'AUTO_AUTO')),
  partner_corrected_contact boolean default false,

  outreach_draft_id text,
  followup_draft_sent_at timestamptz,
  gmail_thread_id text,
  sent_at_detected timestamptz,

  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

---

## Migration 10 — Contact Discovery Log

Tracks accuracy of the auto contact finder over time.

```sql
create table contact_discovery_log (
  id uuid primary key default uuid_generate_v4(),
  publisher_domain text not null,
  discovered_email text,
  was_correct boolean,
  corrected_to text,
  run_number int,
  created_at timestamptz default now()
);
```

---

## Migration 11 — Prompt Versions

A/B testing for outreach email prompts.

```sql
create table prompt_versions (
  id uuid primary key default uuid_generate_v4(),
  prompt_text text not null,
  send_count int default 0,
  response_count int default 0,
  response_rate float default 0,
  active boolean default false,
  created_at timestamptz default now()
);
```

---

## Migration 12 — Music Library

Licensed background tracks for video generation.

```sql
create table music_library (
  id uuid primary key default uuid_generate_v4(),
  title text not null,
  artist text,
  mood text[],
  bpm int,
  duration_sec int,
  license text not null check (license in ('CC0', 'PIXABAY_COMMERCIAL', 'YAL_NO_ATTRIBUTION')),
  file_url text,
  source_url text,
  created_at timestamptz default now()
);
```

---

## Migration 13 — Music Mood Map

Maps book aesthetic tags to music moods.

```sql
create table music_mood_map (
  id uuid primary key default uuid_generate_v4(),
  aesthetic_tag text not null,
  music_mood text not null
);

-- Seed the mood mappings
insert into music_mood_map (aesthetic_tag, music_mood) values
  ('dark academia', 'intense'),
  ('cozy', 'cozy'),
  ('romantasy', 'epic'),
  ('dark romance', 'intense'),
  ('contemporary romance', 'romantic'),
  ('fantasy', 'epic'),
  ('paranormal', 'dreamy'),
  ('small town', 'cozy'),
  ('enemies to lovers', 'intense'),
  ('slow burn', 'dreamy');
```

---

## Migration 14 — Moderation Log

Audit trail for every moderation decision made by a human.

```sql
create table moderation_log (
  id uuid primary key default uuid_generate_v4(),
  campaign_id uuid references campaigns(id) on delete cascade,
  gate text not null check (gate in ('SCRIPT', 'VIDEO')),
  result text not null check (result in ('PASSED', 'FAILED', 'OVERRIDDEN', 'REJECTED', 'EDIT_REQUESTED')),
  system_flags jsonb,
  reviewed_by uuid,
  human_decision text check (human_decision in ('OVERRIDE', 'EDIT', 'REJECT')),
  human_note text,
  created_at timestamptz default now()
);
```

---

## Migration 15 — Seed Books

Known BookTok titles pre-loaded to give the system a starting point before discovery runs.

```sql
create table seed_books (
  id uuid primary key default uuid_generate_v4(),
  title text not null,
  author text not null,
  isbn text,
  genre text,
  notes text,
  added_at timestamptz default now()
);
```

---

## Migration 16 — UI Feedback

Partner can leave notes on any screen to flag issues or missing features.

```sql
create table ui_feedback (
  id uuid primary key default uuid_generate_v4(),
  tenant_id uuid references tenants(id) on delete cascade,
  screen text,
  note text not null,
  resolved boolean default false,
  created_at timestamptz default now()
);
```

---

## Migration 17 — Row Level Security

This locks each tenant's data so they can only see their own records.
Run this after all tables are created.

```sql
-- Enable RLS on all tables
alter table books enable row level security;
alter table campaigns enable row level security;
alter table campaign_parts enable row level security;
alter table affiliate_links enable row level security;
alter table publisher_licenses enable row level security;
alter table book_sources enable row level security;
alter table moderation_log enable row level security;
alter table ui_feedback enable row level security;
alter table user_roles enable row level security;

-- Books policy
create policy "tenant_isolation_books" on books
  using (tenant_id = (select tenant_id from user_roles where user_id = auth.uid() limit 1));

-- Campaigns policy
create policy "tenant_isolation_campaigns" on campaigns
  using (book_id in (
    select id from books where tenant_id = (
      select tenant_id from user_roles where user_id = auth.uid() limit 1
    )
  ));

-- Publisher licenses policy
create policy "tenant_isolation_licenses" on publisher_licenses
  using (tenant_id = (select tenant_id from user_roles where user_id = auth.uid() limit 1));

-- Affiliate links policy
create policy "tenant_isolation_affiliate" on affiliate_links
  using (tenant_id = (select tenant_id from user_roles where user_id = auth.uid() limit 1));

-- UI feedback policy
create policy "tenant_isolation_feedback" on ui_feedback
  using (tenant_id = (select tenant_id from user_roles where user_id = auth.uid() limit 1));
```

---

## Migration 18 — First Tenant and Owner User

After running all migrations, create your first tenant record.
Replace the values in quotes with your own details.

```sql
-- Create your tenant
insert into tenants (name, associate_tag)
values ('ReelForge', 'YOUR-AMAZON-ASSOCIATE-TAG')
returning id;
```

**Copy the UUID that comes back** — you'll need it for the next step.

Then go to **Authentication → Users** in Supabase dashboard, create your user account,
copy the user UUID, and run:

```sql
-- Replace both UUIDs with your actual values
insert into user_roles (tenant_id, user_id, role)
values (
  'PASTE-TENANT-UUID-HERE',
  'PASTE-USER-UUID-HERE',
  'OWNER'
);
```

---

## Verification

After all migrations, run this to confirm all tables exist:

```sql
select table_name
from information_schema.tables
where table_schema = 'public'
order by table_name;
```

You should see 16 tables listed.

---

## What's Next

**Step 1-2:** Seed the `seed_books` table with 20 known BookTok titles
**Step 1-3:** Enable Supabase Auth and test the login flow
