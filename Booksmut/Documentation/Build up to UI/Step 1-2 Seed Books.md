# Step 1-2: Seed the BookTok Starter Library

**Purpose:** Pre-load 20 known BookTok titles into the `seed_books` table. This gives
the discovery pipeline a warm-start list to enrich and score before the automated
fetchers (NYT + Hardcover) kick off in Phase 2.

**Time:** ~5 minutes

---

## How to run this

1. Go to your Supabase project dashboard
2. In the left sidebar, click **SQL Editor**
3. Click **New query**
4. Paste the entire block below
5. Click **Run** (or press Ctrl+Enter)
6. Confirm it says "Success"

---

## The SQL

Paste this entire block as one query — all 20 inserts run together.

```sql
insert into seed_books (title, author, isbn, genre, notes) values

-- Romantasy (most BookTok traffic here)
('A Court of Thorns and Roses',      'Sarah J. Maas',          '9781619634442', 'romantasy',              'ACOTAR series #1 — enormous series following, must-have'),
('A Court of Mist and Fury',         'Sarah J. Maas',          '9781619634497', 'romantasy',              'ACOTAR #2 — consistently ranked higher than book 1 on BookTok'),
('Fourth Wing',                       'Rebecca Yarros',          '9781649374042', 'romantasy',              'Dragon rider college; series exploded on TikTok 2023'),
('Iron Flame',                        'Rebecca Yarros',          '9781649374172', 'romantasy',              'Fourth Wing #2 — same fandom, massive pre-orders'),
('From Blood and Ash',               'Jennifer L. Armentrout', '9781952457302', 'romantasy',              'Blood and Ash #1 — indie published, TikTok made it mainstream'),
('Powerless',                         'Lauren Roberts',          '9781665954815', 'romantasy',              'Powerless #1 — YA crossover, strong trope overlap with ACOTAR'),
('The Cruel Prince',                 'Holly Black',             '9780316310314', 'romantasy',              'Folk of the Air #1 — fae enemies-to-lovers, gateway romantasy'),
('Kingdom of the Wicked',            'Kerri Maniscalco',       '9780316428439', 'dark romantasy',         'Demon love interest, dark academia aesthetic, Italian setting'),
('A Shadow in the Ember',            'Jennifer L. Armentrout', '9781952457586', 'romantasy',              'Flesh and Fire #1 — JLA prequel series, same reader base'),

-- Dark romance
('Haunting Adeline',                 'H.D. Carlton',           NULL,            'dark romance',           'Cat and Mouse #1 — one of the most viral dark romance titles on TikTok'),
('Twisted Love',                     'Ana Huang',              '9781728278131', 'dark romance / contemporary', 'Twisted #1 — billionaire trope, massive series following'),

-- Contemporary romance
('It Ends with Us',                  'Colleen Hoover',         '9781501110368', 'contemporary romance',   'CoHo flagship title — movie release drove second wave of BookTok traffic'),
('Ugly Love',                        'Colleen Hoover',         '9781476753201', 'contemporary romance',   'CoHo — FWB to lovers, extremely quotable, heavy TikTok presence'),
('Icebreaker',                       'Hannah Grace',           '9781668026038', 'contemporary romance',   'Hockey romance — trope exploded post-2022, still trending'),
('The Spanish Love Deception',       'Elena Armas',            '9781982179342', 'contemporary romance',   'Fake dating, slow burn — strong international BookTok crossover'),
('Beach Read',                       'Emily Henry',            '9780593098813', 'contemporary romance',   'Emily Henry debut — sunshine/grumpy writer trope, beach aesthetic'),
('People We Meet on Vacation',       'Emily Henry',            '9780593334836', 'contemporary romance',   'Emily Henry — friends to lovers, travel aesthetic, strong summer push'),
('Book Lovers',                      'Emily Henry',            '9780593334874', 'contemporary romance',   'Emily Henry — BookTok meta-humor, bookish audience loves the premise'),
('Happy Place',                      'Emily Henry',            '9780593441282', 'contemporary romance',   'Emily Henry — fake relationship, group of friends, cottage aesthetic'),

-- Cross-genre / hybrid
('Red, White & Royal Blue',          'Casey McQuiston',        '9781250316776', 'contemporary romance',   'M/M political romance — movie release boosted second-wave traffic');
```

---

## Verify the insert worked

Run this in a new query to confirm all 20 rows landed:

```sql
select title, author, genre
from seed_books
order by genre, title;
```

You should see 20 rows grouped by genre.

---

## What these titles are used for

In Phase 2, the discovery pipeline will pull these titles into the main `books` table,
enrich them with cover images and metadata (Google Books API + Hardcover), score them,
and queue the highest-scoring ones for video generation.

They're a "known good" starting list — real titles that are already proven BookTok performers,
so the pipeline has something to work with before the automated weekly discovery runs.

---

## What's Next

**Step 1-3:** Enable Supabase Auth and test the login flow
**Phase 2:** Build the discovery Cloud Functions (NYT Books fetcher + Hardcover GraphQL fetcher)
