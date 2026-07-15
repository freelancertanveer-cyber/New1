# SaaStr Annual 2026 SMB Sponsor Outreach — Operating Manual

## Target pool
22 mid-market SaaS sponsors from SaaStr Annual 2026.

Excluded: enterprise (Salesforce, Google Cloud, Vercel, Rippling, Okta, TikTok, Booking, PayPal-tier), AI SDR competitors (Artisan, Qualified, Aurasell, Reevo, Momentum, Vivun, Openprise, Crustdata, Leads Per Hour), and irrelevant categories (HR/payroll, telco, unknown micro).

## The universal pitch angle

Every SaaStr sponsor faces the same anxiety: **they just committed $30k-$200k on a sponsor package, and booth ROI is random**. Their CMO/CRO is quietly sweating whether pre-event outbound is warmed enough.

You solve that. Deliver pre-warmed attendee list segmented by their ICP, run outbound in the 4 weeks pre-event, book warm meetings to happen on-site.

**One hook line that scales:** "Every SaaStr sponsor I talked to last year said the same thing — booth traffic is random, and post-event follow-up is a mess. We fix the front end."

## Weekly cadence (3 weeks total)

### Week 1 — Enrichment (Monday-Wednesday)
- Open the CSV
- For rows marked HIGH priority (7 companies): find founder + CMO on LinkedIn Sales Nav
- Guess email pattern from company domain (firstname@, first.last@, flast@)
- Verify emails via Hunter or NeverBounce
- Update CSV status column: enriched

### Week 1 — Outreach (Thursday-Friday)
- Send Email 1 to all 7 HIGH priority (personalized with company-specific hook from CSV "Pitch Hook" column)
- Log send date in CSV

### Week 2 — Bump + expand
- Send Email 2 (bump) to Week 1 batch on Day 3
- Enrich MEDIUM priority (11 companies): same process
- Send Email 1 to MEDIUM batch

### Week 3 — Reframe + close
- Send Email 3 (reframe) to Week 1 batch on Day 7
- Send Email 2 (bump) to Week 2 batch
- Send Email 4 (close loop) to Week 1 batch on Day 10
- Enrich + start LOW priority if bandwidth allows

## Email skeleton (swap company + hook per row)

### Email 1
```
Hey {firstName},

Saw {Company} is on the SaaStr Annual 2026 sponsor list. Big spend, and the ROI clock starts May 12.

{One-line reference to their pain from CSV}

Every SaaStr sponsor I talked to last year said the same thing: booth traffic is random, and post-event follow-up is a mess. We fix the front end. Pull the exact attendee company list, run pre-event outbound in the 4 weeks leading up, book warm meetings on-site.

One SaaS sponsor last year hit 47 pre-booked meetings vs 12 walk-ins.

Want to see what the pre-event target list would look like for {Company}'s ICP?

Fred
```

### Email 2 (Day 3)
```
hey, bumping this. still 5 weeks out from Annual, plenty of room to book warm meetings if we start now.

Fred
```

### Email 3 (Day 7)
```
Different angle in case pre-event outbound isn't the priority.

If bandwidth is the blocker year-round (data + copy + inboxes + reply handling), we run the whole outbound engine end to end for a few SaaS teams. Google Maps sourcing, monthly fresh ICP flow, ~500k sends/mo through pre-warmed infra. Engine trains on your cloud so you own it.

Same 3-per-1K benchmark we hit for others in cooked markets.

Worth 15 min?

Fred
```

### Email 4 (Day 10)
```
hey, closing this out. door's open when the timing works.

Fred
```

## Success metric

Realistic for a 22-company batch:
- Reply rate: 8-15% (small niche, warm signal = SaaStr sponsor)
- Meetings booked: 2-5 from batch
- Deals closed: 1-2 (needs 30-60 day sales cycle)

If you close 1 SaaS sponsor at $2k setup + $300/mo inbox retainer, batch pays for itself 3x over.

## Progress tracking

Update CSV `Status` column after each action:
- `not_started`
- `enriched`
- `email_1_sent`
- `email_2_sent`
- `email_3_sent`
- `email_4_sent`
- `replied`
- `meeting_booked`
- `closed_won`
- `closed_lost`

Check weekly. Kill sequence on `replied` (move to manual thread).

## What NOT to do

- Don't touch Salesforce, Google Cloud, Vercel, Rippling, Okta, TikTok, Booking, Worldpay, Revolut, TaskUs, Papaya, Justworks, TriNet, Deluxe, PayPal-tier. Wrong buyer, procurement chain, calendar impossible.
- Don't pitch AI SDR competitors (Artisan, Qualified, Aurasell, Reevo, Momentum, Vivun). They sell what you sell. Wasted send.
- Don't over-personalize. Peer voice + one specific hook per company is enough. Long research per lead kills the whole cadence.
