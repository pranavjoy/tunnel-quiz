# The Tunnel & Quiz - site + booking system

Static site on Cloudflare Pages, bookings stored in D1, confirmation
emails via Resend. Everything open source / standard tooling; the only
accounts you need are Cloudflare (free) and Resend (free tier: 100
emails/day, 3000/month).

## Layout

    public/               static site (index.html, posters.html, img/)
    functions/api/        Pages Functions -> /api/bookings endpoint
    schema.sql            D1 table
    wrangler.toml         Cloudflare config

## Deploy via GitHub (recommended)

This repo is already committed on branch `main`. Push it, connect it,
done. Every later `git push` deploys automatically; branches get
preview URLs.

### 1. Push to GitHub

Create an empty repo at github.com (private is fine, no README), then:

    git remote add origin git@github.com:YOUR_USER/tunnel-quiz.git
    git push -u origin main

(HTTPS remote works too. To put your own name on the commit first:
`git commit --amend --reset-author` after setting git config.)

### 2. Create the database

    npm install -g wrangler     # or npx wrangler
    wrangler login
    wrangler d1 create tunnel-quiz
    wrangler d1 execute tunnel-quiz --remote --file=schema.sql

### 3. Connect Cloudflare Pages to the repo

In the Cloudflare dashboard:

1. Workers & Pages -> Create -> Pages -> **Connect to Git**
2. Authorize GitHub, select the `tunnel-quiz` repo
3. Build settings:
   - Framework preset: **None**
   - Build command: leave **empty**
   - Build output directory: **public**
4. Save and Deploy. The `functions/` directory is picked up
   automatically; the first deploy will work but /api/bookings will
   error until the bindings below exist.

### 4. Bindings, variables, secrets

Pages project -> Settings:

- **Bindings** -> Add -> D1 database
  - Variable name: `DB`
  - Database: `tunnel-quiz`
- **Variables and secrets**:
  - `RESEND_API_KEY` (type Secret) from resend.com
  - `FROM_EMAIL` e.g. `The Tunnel & Quiz <quiz@yourdomain.nl>` (optional)
  - `NOTIFY_EMAIL` your address, BCC on every booking (optional)
  - `TABLE_LIMIT` max teams per night, default 12 (optional)

Then Deployments -> Retry deployment so the bindings take effect.

### 5. Test

Open the .pages.dev URL, book a table, then:

    wrangler d1 execute tunnel-quiz --remote \
      --command "SELECT * FROM bookings"

## Deploy without GitHub (fallback)

    wrangler pages deploy

from the project root does a direct upload. Same bindings apply. If you
prefer wiring D1 through wrangler.toml instead of the dashboard,
uncomment the d1 block there and paste the real database_id.

## Resend notes

- Without a verified domain, Resend only delivers from
  onboarding@resend.dev **to the email address that owns the Resend
  account**. Fine for testing, useless for guests. Verify a domain
  (Resend -> Domains -> add DNS records) before the first real quiz
  night, then set FROM_EMAIL.
- The booking is saved even if the email fails; the page tells the
  guest to screenshot their confirmation in that case.

## Seeing bookings

    wrangler d1 execute tunnel-quiz --remote \
      --command "SELECT quiz_date, team, captain, email, team_size FROM bookings ORDER BY quiz_date, created_at"

## Privacy (worth 2 minutes)

You are storing names and emails of EU residents: keep it minimal (this
schema already is), mention it in one line on the site if you want to be
tidy, and clear old rows now and then:

    wrangler d1 execute tunnel-quiz --remote \
      --command "DELETE FROM bookings WHERE quiz_date < date('now','-60 days')"

## Fonts

Brand display face is Brigends Expanded (licensed). The site falls back
to Anybody Expanded from Google Fonts. If the bar owns the font files,
drop a woff2 in public/fonts/ and uncomment the @font-face block at the
top of index.html and posters.html.
