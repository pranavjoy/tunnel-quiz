# The Tunnel Quiz - site + booking system

Static site on Cloudflare Pages, bookings stored in D1, confirmation
emails via Resend. Everything open source / standard tooling; the only
accounts you need are Cloudflare (free) and Resend (free tier: 100
emails/day, 3000/month).

## Layout

    public/               static site (index.html, posters.html, img/)
    functions/api/        Pages Functions -> /api/bookings endpoint
    schema.sql            D1 table
    wrangler.toml         Cloudflare config

## Deploy (one time, ~10 minutes)

    npm install -g wrangler        # or use npx wrangler
    wrangler login

    # 1. create the database and copy its id into wrangler.toml
    wrangler d1 create tunnel-quiz
    #   -> paste the printed database_id into wrangler.toml

    # 2. create the table
    wrangler d1 execute tunnel-quiz --remote --file=schema.sql

    # 3. deploy (run from the project root)
    wrangler pages deploy

    # 4. secrets and settings
    wrangler pages secret put RESEND_API_KEY --project-name tunnel-quiz

Then in the Cloudflare dashboard (Pages -> tunnel-quiz -> Settings ->
Environment variables) optionally set:

    FROM_EMAIL    The Tunnel Quiz <quiz@yourdomain.nl>
    NOTIFY_EMAIL  you@yourdomain.nl   (BCC on every booking)
    TABLE_LIMIT   12                  (max teams per night)

Redeploys after the first one are just `wrangler pages deploy`.

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
