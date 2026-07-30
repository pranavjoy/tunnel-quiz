/**
 * POST /api/bookings
 * Body: { team, captain, email, date (YYYY-MM-DD), size (1-6) }
 *
 * Bindings (set in Cloudflare Pages project settings):
 *   DB               D1 database (see schema.sql)
 *   RESEND_API_KEY   secret, from resend.com
 *   FROM_EMAIL       e.g. "The Tunnel Quiz <quiz@yourdomain.nl>"
 *                    (falls back to onboarding@resend.dev for testing)
 *   NOTIFY_EMAIL     optional, gets a copy of every booking
 *   TABLE_LIMIT      optional, max teams per night (default 12)
 */

const ANCHOR_UTC = Date.UTC(2026, 7, 12); // Wed 12 Aug 2026
const MS_PER_DAY = 86400000;

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function isValidQuizDate(dateStr) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return false;
  const t = Date.parse(dateStr + 'T12:00:00Z');
  if (Number.isNaN(t)) return false;
  const daysFromAnchor = Math.round((t - ANCHOR_UTC - 12 * 3600000) / MS_PER_DAY);
  const today = new Date();
  const todayUtc = Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate());
  // Must be on the biweekly Wednesday cadence and not in the past.
  return daysFromAnchor >= 0 && daysFromAnchor % 14 === 0 && t >= todayUtc;
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

function confirmationHtml({ team, captain, dateLabel, size }) {
  const e = escapeHtml;
  return `<!DOCTYPE html>
<html><body style="margin:0;background:#131313;padding:32px 16px;font-family:Arial,Helvetica,sans-serif;">
  <div style="max-width:520px;margin:0 auto;background:#EBE7C8;border-radius:8px;overflow:hidden;">
    <div style="background:#EA6F1C;padding:28px;text-align:center;">
      <div style="font-size:30px;font-weight:900;letter-spacing:1px;color:#131313;text-transform:uppercase;">Seat saved.</div>
    </div>
    <div style="padding:28px;color:#3B2A1F;">
      <p style="margin:0 0 16px;font-size:16px;">Hi ${e(captain)},</p>
      <p style="margin:0 0 16px;font-size:16px;">
        <strong>${e(team)}</strong> has a table for <strong>${size}</strong> at The Tunnel Quiz on
        <strong>${e(dateLabel)}</strong>.
      </p>
      <p style="margin:0 0 16px;font-size:15px;">
        Doors from 19:30, first question at 20:00 sharp. Three rounds, then the jackpot.
        Six per team, max. Free entry.
      </p>
      <p style="margin:0;font-size:15px;">
        The Tunnel &amp; Co. · Bilderdijkstraat 186, Amsterdam<br>
        <a href="https://maps.google.com/?q=The+Tunnel+%26+Co,+Bilderdijkstraat+186,+Amsterdam" style="color:#EA6F1C;">Open in Google Maps</a>
      </p>
    </div>
    <div style="background:#103B32;padding:18px;text-align:center;color:#EBE7C8;font-size:12px;letter-spacing:2px;text-transform:uppercase;">
      Think. Sip. Repeat.
    </div>
  </div>
</body></html>`;
}

async function sendEmail(env, booking) {
  if (!env.RESEND_API_KEY) return false;
  const dateLabel = new Intl.DateTimeFormat('en-GB', {
    weekday: 'long', day: 'numeric', month: 'long', timeZone: 'UTC',
  }).format(new Date(booking.date + 'T12:00:00Z'));

  const payload = {
    from: env.FROM_EMAIL || 'The Tunnel Quiz <onboarding@resend.dev>',
    to: [booking.email],
    subject: `Seat saved: ${booking.team}, ${dateLabel} 20:00`,
    html: confirmationHtml({ ...booking, dateLabel }),
  };
  if (env.NOTIFY_EMAIL) payload.bcc = [env.NOTIFY_EMAIL];

  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  return res.ok;
}

export async function onRequestPost(context) {
  const { request, env } = context;

  let data;
  try {
    data = await request.json();
  } catch {
    return json({ error: 'Send the booking as JSON.' }, 400);
  }

  const team = String(data.team || '').trim().slice(0, 60);
  const captain = String(data.captain || '').trim().slice(0, 80);
  const email = String(data.email || '').trim().slice(0, 120).toLowerCase();
  const date = String(data.date || '').trim();
  const size = Number.parseInt(data.size, 10);

  if (!team) return json({ error: 'Your team needs a name.' }, 400);
  if (!captain) return json({ error: 'Every team needs a captain.' }, 400);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ error: 'That email does not look right.' }, 400);
  if (!Number.isInteger(size) || size < 1 || size > 6) return json({ error: 'Teams are 1 to 6 players. Six heads max.' }, 400);
  if (!isValidQuizDate(date)) return json({ error: 'Pick one of the listed quiz nights.' }, 400);

  const limit = Number.parseInt(env.TABLE_LIMIT || '12', 10);

  try {
    const { c } = await env.DB
      .prepare('SELECT COUNT(*) AS c FROM bookings WHERE quiz_date = ?')
      .bind(date)
      .first();
    if (c >= limit) {
      return json({ error: 'That night is fully booked. Pick the next one, or chance it as a walk-in.' }, 409);
    }

    await env.DB
      .prepare('INSERT INTO bookings (team, captain, email, quiz_date, team_size) VALUES (?, ?, ?, ?, ?)')
      .bind(team, captain, email, date, size)
      .run();
  } catch (err) {
    if (String(err).includes('UNIQUE')) {
      return json({ error: 'That email already has a table for this quiz night.' }, 409);
    }
    return json({ error: 'Could not save the booking. Try again in a minute.' }, 500);
  }

  let emailSent = false;
  try {
    emailSent = await sendEmail(env, { team, captain, email, date, size });
  } catch {
    // Booking is saved; email failure should not fail the request.
  }

  return json({ ok: true, emailSent });
}
