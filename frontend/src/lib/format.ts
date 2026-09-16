const CURRENCY_SYMBOL: Record<string, string> = { INR: '₹', USD: '$', EUR: '€', GBP: '£', AED: 'د.إ', SGD: 'S$' }

export function symbol(currency = 'INR') {
  return CURRENCY_SYMBOL[currency] ?? currency + ' '
}

/** Compact money: INR uses lakh/crore, everything else uses K/M/B. */
export function money(value: number | string | null | undefined, currency = 'INR', digits = 1): string {
  const v = Number(value ?? 0)
  const s = symbol(currency)
  const abs = Math.abs(v)
  const sign = v < 0 ? '-' : ''
  if (currency === 'INR') {
    if (abs >= 1e7) return `${sign}${s}${(abs / 1e7).toFixed(digits)} Cr`
    if (abs >= 1e5) return `${sign}${s}${(abs / 1e5).toFixed(digits)} L`
    if (abs >= 1e3) return `${sign}${s}${(abs / 1e3).toFixed(digits)}K`
    return `${sign}${s}${abs.toFixed(0)}`
  }
  if (abs >= 1e9) return `${sign}${s}${(abs / 1e9).toFixed(digits)}B`
  if (abs >= 1e6) return `${sign}${s}${(abs / 1e6).toFixed(digits)}M`
  if (abs >= 1e3) return `${sign}${s}${(abs / 1e3).toFixed(digits)}K`
  return `${sign}${s}${abs.toFixed(0)}`
}

export function compact(value: number | string | null | undefined, digits = 1): string {
  const v = Number(value ?? 0)
  const abs = Math.abs(v)
  if (abs >= 1e9) return (v / 1e9).toFixed(digits) + 'B'
  if (abs >= 1e6) return (v / 1e6).toFixed(digits) + 'M'
  if (abs >= 1e3) return (v / 1e3).toFixed(digits) + 'K'
  return Math.round(v).toLocaleString()
}

export function num(value: number | string | null | undefined) {
  return Math.round(Number(value ?? 0)).toLocaleString()
}

export function pct(value: number | string | null | undefined, digits = 1) {
  return `${Number(value ?? 0).toFixed(digits)}%`
}

export function signedPct(value: number | null | undefined, digits = 1) {
  const v = Number(value ?? 0)
  return `${v > 0 ? '+' : ''}${v.toFixed(digits)}%`
}

export function relTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  const diff = (Date.now() - new Date(iso).getTime()) / 1000
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  if (diff < 86400 * 7) return `${Math.floor(diff / 86400)}d ago`
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

export function shortDate(iso: string | null | undefined) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

export function dayLabel(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

export function title(s: string | null | undefined) {
  return (s ?? '').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export const CHANNEL_LABEL: Record<string, string> = {
  meta: 'Meta', google_search: 'Google Search', google_display: 'Google Display', youtube: 'YouTube', linkedin: 'LinkedIn',
  tiktok: 'TikTok', x: 'X', outbound: 'Outbound', organic: 'Organic / SEO', landing_page: 'Landing page',
}
export const channelLabel = (c: string) => CHANNEL_LABEL[c] ?? title(c)

/** Fixed categorical slot per channel so a channel never changes colour between views. */
export const CHANNEL_COLOR: Record<string, string> = {
  outbound: 'var(--series-1)', google_search: 'var(--series-2)', linkedin: 'var(--series-3)', meta: 'var(--series-4)',
  youtube: 'var(--series-5)', organic: 'var(--series-6)', google_display: 'var(--series-7)', tiktok: 'var(--series-7)', x: 'var(--series-7)',
}
export const channelColor = (c: string) => CHANNEL_COLOR[c] ?? 'var(--series-7)'

/* ---------------------------------------------------------------------------
 * Plain language
 * The product's own vocabulary is full of jargon (CAC, ROAS, ICP, MQL). One map
 * so every screen calls the same thing by the same plain name, plus a one-line
 * explanation surfaced by the <Explain> tooltip.
 * ------------------------------------------------------------------------- */
export const PLAIN: Record<string, { label: string; short?: string; explain: string }> = {
  revenue:        { label: 'Money made',         explain: 'Revenue from deals that actually closed in this period.' },
  pipeline:       { label: 'Deals in progress',  explain: 'Total value of open opportunities. Not money yet — deals you are working on.' },
  spend:          { label: 'Money spent',        explain: 'What you paid for ads and marketing tools in this period.' },
  cac:            { label: 'Cost per customer',  short: 'CAC', explain: 'Marketing spend divided by new customers won. Lower is better.' },
  cost_per_lead:  { label: 'Cost per lead',      short: 'CPL', explain: 'Marketing spend divided by leads generated. Lower is better.' },
  cpl:            { label: 'Cost per lead',      short: 'CPL', explain: 'Marketing spend divided by leads generated. Lower is better.' },
  roas:           { label: 'Return on ad spend', short: 'ROAS', explain: 'Money made for every ₹1 spent. 3x means ₹3 back for every ₹1 in.' },
  roi_pct:        { label: 'Marketing return',   explain: 'Profit from marketing as a percentage of what you spent.' },
  qualified_leads:{ label: 'Ready-to-talk leads', explain: 'People who showed real buying interest and are worth a sales conversation.' },
  leads:          { label: 'Leads',              explain: 'People who gave you their details or replied with interest.' },
  meetings:       { label: 'Meetings booked',    explain: 'Sales calls actually on the calendar.' },
  customers:      { label: 'New customers',      explain: 'Deals that closed and started paying.' },
  ltv:            { label: 'Customer value',     short: 'LTV', explain: 'How much an average customer is worth to you over their whole lifetime.' },
  ltv_to_cac:     { label: 'Value vs. cost',     short: 'LTV:CAC', explain: 'Customer value divided by what it cost to win them. Above 3x is healthy.' },
  payback_months: { label: 'Time to break even', explain: 'How many months until a customer pays back what you spent to win them.' },
  gross_margin_pct: { label: 'Gross margin',     explain: 'The share of each sale left after the direct cost of delivering it.' },
  icp:            { label: 'Target customer',    short: 'ICP', explain: 'Ideal Customer Profile — the kind of company most likely to buy from you.' },
  tier:           { label: 'Priority',           explain: 'Tier 1 = best fit, chase first. Tier 3 = weak fit, low priority.' },
  fit_score:      { label: 'Match score',        explain: 'How well this company matches your target customer, 0–100.' },
  attribution:    { label: 'What drove the sale', explain: 'Which channels touched a customer before they bought, and how much credit each gets.' },
  mql:            { label: 'Interested lead',    short: 'MQL', explain: 'Marketing Qualified Lead — engaged enough that marketing thinks sales should look.' },
  sql:            { label: 'Sales-ready lead',   short: 'SQL', explain: 'Sales Qualified Lead — sales has confirmed this is a real opportunity.' },
  sequence:       { label: 'Email sequence',     explain: 'A planned series of emails sent over days, which stops as soon as someone replies.' },
  ctr:            { label: 'Click rate',         short: 'CTR', explain: 'Share of people who saw the ad and clicked it.' },
  cvr:            { label: 'Sign-up rate',       short: 'CVR', explain: 'Share of page visitors who filled in the form.' },
}

export const plainLabel = (key: string, fallback?: string) => PLAIN[key]?.label ?? fallback ?? title(key)
export const explainOf = (key: string) => PLAIN[key]?.explain
