"""
Catalogue of every third-party API the AI GTM OS can connect to, with everything
needed to actually acquire it: prerequisites, difficulty, lead time, cost model,
step-by-step signup path and the .env keys it fills.

Consumed by `tools/generate_api_workbook.py` to build the Excel workbook.

PRICING IS INDICATIVE (USD/month, list price, small-team tier, as of early 2026).
Always confirm on the vendor's pricing page — these move.
"""
from __future__ import annotations

# Phase = when to acquire it. See "Start Here" sheet.
#   P0  Day 1        — nothing runs without it
#   P1  Week 1       — the wedge: outbound + one paid channel + CRM + revenue truth
#   P2  Week 2-4     — second channel, research, deliverability, approvals
#   P3  Month 2-3    — scale: video/creative, more social, SEO suites, lifecycle
#   P4  Later / opt  — enterprise contracts, nice-to-haves, alternatives

# Need = Required | Recommended | Optional | Alternative
#   "Alternative" = you only need ONE of the group (pick-one), noted in Gotchas.

# Difficulty = Instant | Easy | Medium | Hard | Enterprise
#   Instant    self-serve key in < 5 min
#   Easy       self-serve, some config (OAuth, service account)
#   Medium     app creation + scopes + a short review, or a paid plan gate
#   Hard       formal application / business verification / platform review
#   Enterprise sales call, contract, annual commit

COLUMNS = [
    ("#", 5), ("Phase", 7), ("Category", 20), ("Provider", 22), ("What it powers", 40),
    ("Need", 13), ("Difficulty", 12), ("Lead time", 14), ("Prerequisite", 34),
    ("Cost model", 26), ("Est. $/mo", 11), ("Free tier", 22), ("Sign-up URL", 42), ("Docs URL", 42),
    ("How to acquire (steps)", 90), (".env keys", 40), ("Gotchas / watch-outs", 60),
    ("Status", 14), ("Owner", 14), ("Target date", 13), ("Notes", 30),
]

# (phase, category, provider, powers, need, difficulty, lead, prereq, cost_model, est_cost,
#  free_tier, signup, docs, steps, env_keys, gotchas)
PROVIDERS: list[tuple] = [

    # ================================================================= P0 — AI core
    ("P0", "AI Models", "Groq",
     "Every agent's reasoning: AI CMO, ICP, copy, replies, decisions",
     "Required", "Instant", "5 minutes", "Email (free tier needs no card)",
     "Free tier, then pay-per-token", 25,
     "Yes - free tier, rate-limited", "https://console.groq.com/keys",
     "https://console.groq.com/docs",
     "1) Sign up at console.groq.com (Google/GitHub login works). 2) API Keys -> Create API Key -> copy it "
     "(shown once). 3) Paste into GROQ_API_KEY in .env. 4) Check which models your key can use: "
     "curl https://api.groq.com/openai/v1/models -H \"Authorization: Bearer $GROQ_API_KEY\" "
     "5) Set GROQ_MODEL (reasoning) and GROQ_WORKER_MODEL (bulk/cheap) to IDs from that list. "
     "6) Restart Django - the sidebar badge flips from 'Demo data' to 'AI is live'. "
     "7) For production volume, add billing in the console to lift the free-tier rate limits.",
     "GROQ_API_KEY, GROQ_MODEL, GROQ_WORKER_MODEL, LLM_PROVIDER",
     "THE FREE TIER IS RATE-LIMITED (requests and tokens per minute) - fine for testing, but running all 38 agents "
     "will hit it. The client retries with backoff (GROQ_MAX_RETRIES), but add billing before scheduling agent runs. "
     "Model IDs change: verify against the /models endpoint rather than trusting a hardcoded name."),

    # ================================================================= P1 — the wedge
    ("P1", "Prospecting", "Apollo.io",
     "Lead Discovery + Lead Enrichment: find and enrich ICP accounts/contacts",
     "Required", "Easy", "Same day", "Work email (blocks free domains)",
     "Seat subscription; API on paid plans", 99,
     "Free plan exists, API limited", "https://app.apollo.io/#/settings/integrations/api",
     "https://docs.apollo.io/reference",
     "1) Sign up with a company email (Gmail/Outlook domains get rejected). 2) Upgrade to a plan with API access "
     "(Basic+ / Professional). 3) Settings -> Integrations -> API -> Create new key. 4) Note your monthly credit "
     "allowance and per-endpoint rate limits. 5) Paste into APOLLO_API_KEY. 6) Confirm on /integrations -> Apollo -> Test connection.",
     "APOLLO_API_KEY",
     "Export/enrichment credits are the real constraint, not rate limits. API access is gated behind paid tiers — "
     "check the current tier before buying."),

    ("P1", "Email Verification", "MillionVerifier",
     "Lead Verification Agent: deliverability gate before any send",
     "Required", "Instant", "5 minutes", "None",
     "Pay-as-you-go credits (no expiry)", 30,
     "100 free credits", "https://www.millionverifier.com",
     "https://developer.millionverifier.com",
     "1) Sign up. 2) Buy a credit pack (10k credits is a cheap start — credits don't expire). 3) Dashboard -> API -> copy key. "
     "4) Paste into MILLIONVERIFIER_API_KEY. 5) Keep EMAIL_VERIFICATION_WATERFALL ordered cheapest-first.",
     "MILLIONVERIFIER_API_KEY, EMAIL_VERIFICATION_WATERFALL",
     "Cheapest of the three verifiers — good default. Pick ONE to start; the waterfall only needs a second "
     "provider once volume justifies it."),

    ("P1", "Email Verification", "ZeroBounce",
     "Lead Verification Agent (waterfall step 1)",
     "Alternative", "Instant", "5 minutes", "None",
     "Credit packs or monthly", 40,
     "100 free/month", "https://www.zerobounce.net",
     "https://www.zerobounce.net/docs/",
     "1) Sign up. 2) Buy credits. 3) API -> copy key. 4) Paste into ZEROBOUNCE_API_KEY.",
     "ZEROBOUNCE_API_KEY",
     "Pick ONE verifier to start (ZeroBounce / NeverBounce / MillionVerifier). Adding all three only helps at scale."),

    ("P1", "Email Verification", "NeverBounce",
     "Lead Verification Agent (waterfall step 2)",
     "Alternative", "Instant", "5 minutes", "None",
     "Pay-as-you-go", 40,
     "1,000 free on signup", "https://app.neverbounce.com",
     "https://developers.neverbounce.com",
     "1) Sign up. 2) Add credits. 3) Account -> API -> generate key. 4) Paste into NEVERBOUNCE_API_KEY.",
     "NEVERBOUNCE_API_KEY",
     "Alternative to MillionVerifier/ZeroBounce — do not buy all three on day one."),

    ("P1", "Outbound Sending", "Instantly",
     "AI Sequence Agent: mailbox rotation, warmup, throttled sends, reply capture",
     "Required", "Medium", "1-2 days setup, 2-3 weeks warmup", "Sending domains + mailboxes",
     "Per-seat + per-mailbox", 97,
     "14-day trial", "https://app.instantly.ai",
     "https://developer.instantly.ai",
     "1) Buy 2-3 lookalike sending domains (NOT your primary domain) e.g. get-acme.com, tryacme.com. "
     "2) Create 2-3 mailboxes per domain in Google Workspace or Microsoft 365. 3) Set SPF, DKIM and DMARC on every domain. "
     "4) Sign up for Instantly, connect all mailboxes, switch warmup ON and leave it for 2-3 weeks before real sends. "
     "5) Settings -> Integrations -> API -> copy key -> INSTANTLY_API_KEY. 6) Keep OUTBOUND_DAILY_LIMIT_PER_MAILBOX at 30-40.",
     "INSTANTLY_API_KEY, OUTBOUND_PROVIDER, OUTBOUND_DAILY_LIMIT_PER_MAILBOX",
     "WARMUP IS THE LONG POLE — start domains + warmup on day 1 even if everything else waits. "
     "Never send cold outbound from your primary domain. Check local law (GDPR/CAN-SPAM/CASL) for your target geos."),

    ("P1", "CRM", "HubSpot",
     "CRM Agent + Attribution: contacts, companies, deals, notes, tasks",
     "Required", "Easy", "30 minutes", "HubSpot account (free tier works)",
     "Free CRM; paid for automation", 0,
     "Free CRM tier is enough", "https://app.hubspot.com",
     "https://developers.hubspot.com/docs/api/overview",
     "1) Create a free HubSpot account. 2) Settings -> Integrations -> Private Apps -> Create private app. "
     "3) Scopes: crm.objects.contacts/companies/deals read+write, crm.schemas read, plus tasks/notes (engagements). "
     "4) Create app -> copy the access token (shown once). 5) Paste into HUBSPOT_ACCESS_TOKEN and set CRM_PROVIDER=hubspot. "
     "6) Test on /integrations -> HubSpot.",
     "HUBSPOT_ACCESS_TOKEN, HUBSPOT_PORTAL_ID, CRM_PROVIDER",
     "Private-app tokens are simpler than OAuth for a single workspace. If you add scopes later you must re-copy the token."),

    ("P1", "Analytics & Revenue", "Stripe",
     "Attribution + Revenue Intelligence: the closed-revenue source of truth",
     "Required", "Instant", "Same day (live keys need KYC)", "Registered business for live mode",
     "% of transactions (no API fee)", 0,
     "Test mode free forever", "https://dashboard.stripe.com/apikeys",
     "https://stripe.com/docs/api",
     "1) Create a Stripe account. 2) Developers -> API keys -> copy the SECRET key (sk_test_ for testing, sk_live_ after "
     "business verification). 3) Developers -> Webhooks -> add endpoint <PUBLIC_API_URL>/api/webhooks/stripe/ -> copy the "
     "signing secret. 4) Paste STRIPE_SECRET_KEY + STRIPE_WEBHOOK_SECRET. 5) Start in test mode with seeded data.",
     "STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET",
     "Use restricted keys (read-only on charges/subscriptions) rather than the full secret key. "
     "Skip if you don't bill through Stripe — use Shopify or CRM closed-won instead."),

    ("P1", "Paid Media", "Google Ads",
     "Paid Media Agent + Autonomous Media Buyer: Search, Display, YouTube",
     "Required", "Hard", "1-3 weeks (token review)", "Google Ads account + Manager (MCC) + billing",
     "Ad spend only; API free", 0,
     "API is free; you pay media", "https://ads.google.com",
     "https://developers.google.com/google-ads/api/docs/start",
     "1) Create a Google Ads account AND a Manager (MCC) account; link the ad account to the MCC. Add billing. "
     "2) In the MCC: Tools -> Setup -> API Center -> apply for a developer token. You start with Test access. "
     "3) Apply for Basic access: describe the tool, your company site, and how you comply with the Required Minimum "
     "Functionality policy. Review typically takes a few business days to ~3 weeks. "
     "4) In Google Cloud Console: create a project, enable the Google Ads API, configure the OAuth consent screen, "
     "create an OAuth client ID (Desktop or Web). "
     "5) Generate a refresh token (OAuth Playground with your own client ID, or the SDK's auth script). "
     "6) Fill GOOGLE_ADS_DEVELOPER_TOKEN, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, LOGIN_CUSTOMER_ID (MCC, digits only), "
     "CUSTOMER_ID (target account, digits only).",
     "GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN, "
     "GOOGLE_ADS_LOGIN_CUSTOMER_ID, GOOGLE_ADS_CUSTOMER_ID",
     "APPLY FOR THE DEVELOPER TOKEN ON DAY 1 — it is the slowest item in Week 1. Test access only works against test "
     "accounts, so you cannot touch real campaigns until Basic access lands. Customer IDs must have dashes stripped."),

    ("P1", "Analytics & Revenue", "Google Analytics 4",
     "Analytics Agent + CRO: traffic, conversions, journey stitching",
     "Recommended", "Easy", "1 hour", "GA4 property + Google Cloud project",
     "Free (GA4 standard)", 0,
     "Free", "https://console.cloud.google.com",
     "https://developers.google.com/analytics/devguides/reporting/data/v1",
     "1) Google Cloud Console -> create/select a project -> enable 'Google Analytics Data API'. "
     "2) IAM -> Service Accounts -> create one -> Keys -> Add key -> JSON -> download. "
     "3) In GA4 Admin -> Property Access Management -> add the service-account email as Viewer. "
     "4) Copy the GA4 property ID (Admin -> Property Settings, numeric). "
     "5) Set GA4_PROPERTY_ID and GOOGLE_SERVICE_ACCOUNT_JSON_PATH (keep the JSON outside git).",
     "GA4_PROPERTY_ID, GOOGLE_SERVICE_ACCOUNT_JSON_PATH, GOOGLE_SERVICE_ACCOUNT_JSON",
     "The same service account can also serve Search Console — reuse it. Never commit the JSON file."),

    ("P1", "Alerts & Ops", "Slack",
     "Compliance + AI CMO: approval requests and 'needs human sign-off' alerts",
     "Recommended", "Easy", "20 minutes", "Slack workspace admin",
     "Free", 0,
     "Free", "https://api.slack.com/apps",
     "https://api.slack.com/quickstart",
     "1) api.slack.com/apps -> Create New App -> From scratch. 2) OAuth & Permissions -> Bot Token Scopes: "
     "chat:write, chat:write.public, channels:read. 3) Install to Workspace -> copy the Bot User OAuth Token (xoxb-...). "
     "4) Invite the bot to your alerts channel. 5) Set SLACK_BOT_TOKEN and SLACK_ALERTS_CHANNEL.",
     "SLACK_BOT_TOKEN, SLACK_ALERTS_CHANNEL, SLACK_SIGNING_SECRET",
     "Without this, approvals live only in the Command Centre — fine for one operator, painful for a team."),

    # ================================================================= P2 — second channel + research
    ("P2", "Paid Media", "Meta Ads (Facebook + Instagram)",
     "Paid Media Agent, Creative Testing, Competitor ad monitoring (Ad Library)",
     "Required", "Hard", "1-4 weeks (verification)", "Meta Business Account + Page + verified business",
     "Ad spend only; API free", 0,
     "API free; you pay media", "https://developers.facebook.com/apps",
     "https://developers.facebook.com/docs/marketing-apis",
     "1) Create a Meta Business Account at business.facebook.com; add your Facebook Page, Instagram account and Ad Account. "
     "2) START BUSINESS VERIFICATION IMMEDIATELY (Business Settings -> Security Centre): you need your legal business "
     "name, registration/incorporation document and a document showing the business address or phone. This is the slow part. "
     "3) developers.facebook.com -> Create App -> type 'Business' -> link it to the Business Account. "
     "4) Add the 'Marketing API' product. Development access works instantly on ad accounts you own. "
     "5) Business Settings -> Users -> System Users -> Add -> Admin -> Generate New Token. Scopes: ads_management, ads_read, "
     "business_management, pages_show_list, pages_manage_posts, instagram_basic, instagram_content_publish. "
     "6) Assign the System User to the Ad Account, Page and Instagram account. "
     "7) For live traffic at scale, submit App Review for Advanced Access on ads_management. "
     "8) Fill META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN, META_AD_ACCOUNT_ID (act_ prefix), META_PAGE_ID, "
     "META_INSTAGRAM_ACCOUNT_ID, META_PIXEL_ID.",
     "META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN, META_AD_ACCOUNT_ID, META_PIXEL_ID, META_PAGE_ID, "
     "META_INSTAGRAM_ACCOUNT_ID, META_API_VERSION",
     "Business Verification gates Advanced Access, WhatsApp Cloud API and the Ad Library — start it the same day you "
     "start Google Ads. Use a System User token (long-lived), never a personal user token. "
     "Ad account ID must keep the 'act_' prefix."),

    ("P2", "SEO & Research", "Firecrawl",
     "Business Intelligence + Competitor Intelligence: crawl site, docs, pricing, competitors",
     "Recommended", "Instant", "5 minutes", "None",
     "Credit-based monthly", 19,
     "500 free credits", "https://firecrawl.dev",
     "https://docs.firecrawl.dev",
     "1) Sign up. 2) Dashboard -> API Keys -> copy. 3) Paste into FIRECRAWL_API_KEY. "
     "4) Run the Business Intelligence Agent to build the knowledge graph from your own site.",
     "FIRECRAWL_API_KEY",
     "This is what turns the knowledge graph from seeded demo data into YOUR business. High leverage for the price."),

    ("P2", "SEO & Research", "Tavily",
     "Market Intelligence + AI Research Agent: live web research for prospect cards",
     "Recommended", "Instant", "5 minutes", "None",
     "Monthly API credits", 30,
     "1,000 free credits/mo", "https://tavily.com",
     "https://docs.tavily.com",
     "1) Sign up. 2) Copy the API key from the dashboard home. 3) Paste into TAVILY_API_KEY.",
     "TAVILY_API_KEY",
     "Built for LLM agents — cleaner results than raw search scraping. Exa is the alternative; you don't need both."),

    ("P2", "SEO & Research", "SerpApi",
     "SEO Agent: SERP rank monitoring and competitor SERP analysis",
     "Recommended", "Instant", "5 minutes", "None",
     "Searches/month", 75,
     "100 free searches/mo", "https://serpapi.com/manage-api-key",
     "https://serpapi.com/search-api",
     "1) Sign up. 2) Dashboard -> API Key -> copy. 3) Paste into SERPAPI_API_KEY.",
     "SERPAPI_API_KEY",
     "DataForSEO is cheaper at volume but clunkier. Start here, switch if SERP tracking becomes your biggest line item."),

    ("P2", "Analytics & Revenue", "Google Search Console",
     "SEO Agent: real ranking + query data for your own domain",
     "Recommended", "Easy", "1 hour (+ up to 48h data lag)", "Verified domain ownership",
     "Free", 0,
     "Free", "https://search.google.com/search-console",
     "https://developers.google.com/webmaster-tools",
     "1) Add and verify your property in Search Console (DNS TXT record is the most robust). "
     "2) Enable the 'Google Search Console API' in the SAME Google Cloud project you used for GA4. "
     "3) Add the GA4 service-account email as a user on the Search Console property. "
     "4) Set GSC_SITE_URL (exactly as shown in Search Console, including https:// and trailing slash where relevant).",
     "GSC_SITE_URL, GOOGLE_SERVICE_ACCOUNT_JSON_PATH",
     "Reuses the GA4 service account — no second key needed. URL string must match the property exactly."),

    ("P2", "Email Marketing", "Resend",
     "Email Marketing + Lifecycle Agent: nurture, newsletters, transactional",
     "Recommended", "Easy", "1 day (DNS)", "A domain you control",
     "Emails/month", 20,
     "3,000 emails/mo free", "https://resend.com/api-keys",
     "https://resend.com/docs",
     "1) Sign up. 2) Domains -> Add domain -> add the DKIM/SPF records to your DNS -> wait for verification. "
     "3) API Keys -> Create -> copy. 4) Set RESEND_API_KEY, ESP_PROVIDER=resend, DEFAULT_FROM_EMAIL.",
     "RESEND_API_KEY, ESP_PROVIDER, DEFAULT_FROM_EMAIL",
     "This is MARKETING email (opted-in lists) — separate from cold outbound, which goes through Instantly on "
     "separate domains. Never mix the two on one domain."),

    ("P2", "Outbound Sending", "Gmail API",
     "Reply Intelligence + AI SDR: read replies, send from the founder's real mailbox",
     "Recommended", "Medium", "1-3 days", "Google Workspace account",
     "Free (Workspace seat)", 0,
     "Free with Workspace", "https://console.cloud.google.com",
     "https://developers.google.com/gmail/api",
     "1) Google Cloud Console -> enable the Gmail API. 2) Configure the OAuth consent screen (Internal if Workspace — "
     "avoids Google verification; External needs review for restricted scopes). "
     "3) Create an OAuth client ID. 4) Consent with scopes gmail.readonly + gmail.send and capture the refresh token. "
     "5) Fill GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN.",
     "GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN",
     "Choose 'Internal' on the consent screen if you're on Workspace — External + restricted scopes triggers a "
     "security assessment that can take weeks. Use Microsoft Graph instead if you're a Microsoft 365 shop."),

    ("P2", "Outbound Sending", "Cal.com",
     "AI SDR: meeting booking links and confirmed-slot capture",
     "Recommended", "Instant", "15 minutes", "Calendar connected",
     "Free self-serve tier", 0,
     "Free tier", "https://app.cal.com/settings/developer/api-keys",
     "https://cal.com/docs/api-reference",
     "1) Sign up, connect Google/Outlook calendar, create an event type. 2) Settings -> Developer -> API Keys -> create. "
     "3) Paste into CAL_COM_API_KEY.",
     "CAL_COM_API_KEY",
     "Calendly is the alternative and needs a paid tier for API access — Cal.com is the cheaper start."),

    ("P2", "Prospecting", "Hunter.io",
     "Waterfall Data Agent: email-pattern fallback when Apollo can't resolve",
     "Recommended", "Instant", "5 minutes", "None",
     "Monthly requests", 49,
     "25 searches/mo free", "https://hunter.io/api-keys",
     "https://hunter.io/api-documentation",
     "1) Sign up. 2) API -> copy key. 3) Paste into HUNTER_API_KEY. 4) Add 'hunter' to ENRICHMENT_WATERFALL.",
     "HUNTER_API_KEY, ENRICHMENT_WATERFALL",
     "Only worth adding once you see Apollo's fill-rate gap in the enrichment log on /prospects."),

    ("P2", "Landing Pages & CMS", "Vercel",
     "Landing Page Agent: deploy generated campaign pages",
     "Optional", "Instant", "15 minutes", "Vercel account + domain",
     "Free hobby tier", 0,
     "Hobby free", "https://vercel.com/account/tokens",
     "https://vercel.com/docs/rest-api",
     "1) Create a Vercel account and a project. 2) Account Settings -> Tokens -> Create. "
     "3) Copy the project ID from Project Settings. 4) Set VERCEL_TOKEN, VERCEL_PROJECT_ID, LANDING_PAGE_DOMAIN.",
     "VERCEL_TOKEN, VERCEL_PROJECT_ID, LANDING_PAGE_DOMAIN",
     "Only needed when you want pages auto-published. Pages render inside the app without this."),

    # ================================================================= P3 — scale
    ("P3", "Paid Media", "LinkedIn Marketing API",
     "Paid Media (LinkedIn Ads), LinkedIn Agent (organic), Lead Gen Forms",
     "Recommended", "Hard", "2-8 weeks (uncertain)", "Company Page + Ad Account + app",
     "Ad spend; API free", 0,
     "API free; you pay media", "https://www.linkedin.com/developers/apps",
     "https://learn.microsoft.com/linkedin/marketing",
     "1) Create a LinkedIn Company Page and a Campaign Manager ad account with billing. "
     "2) linkedin.com/developers -> Create App -> associate it with the Company Page -> verify the Page (an admin clicks the link). "
     "3) Products tab -> request 'Advertising API' (and 'Community Management API' for organic posting). "
     "Each is a separate application with a business justification and a review. "
     "4) Auth tab -> copy Client ID/Secret; run the 3-legged OAuth flow to get an access token "
     "(scopes: r_ads, rw_ads, r_ads_reporting, w_organization_social). "
     "5) Fill LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_ACCESS_TOKEN, LINKEDIN_AD_ACCOUNT_ID, LINKEDIN_ORGANIZATION_ID.",
     "LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_ACCESS_TOKEN, LINKEDIN_AD_ACCOUNT_ID, LINKEDIN_ORGANIZATION_ID",
     "THE LEAST PREDICTABLE APPROVAL of all of these — apply early, expect back-and-forth, and have a manual fallback. "
     "Access tokens expire (~60 days); implement refresh. Never scrape LinkedIn — it will get accounts banned."),

    ("P3", "Creative Generation", "ElevenLabs",
     "AI Video Agent: voiceover for ad variants",
     "Optional", "Instant", "5 minutes", "None",
     "Characters/month", 22,
     "10k chars/mo free", "https://elevenlabs.io",
     "https://elevenlabs.io/docs",
     "1) Sign up. 2) Profile -> API Key -> copy. 3) Paste into ELEVENLABS_API_KEY.",
     "ELEVENLABS_API_KEY",
     "Check the commercial-use terms on your tier before putting generated voice into paid ads."),

    ("P3", "Creative Generation", "fal.ai",
     "AI Creative Director + Video Agent: image and video variant generation",
     "Optional", "Instant", "5 minutes", "None",
     "Pay-per-second compute", 50,
     "Small free credit", "https://fal.ai/dashboard/keys",
     "https://fal.ai/docs",
     "1) Sign up. 2) Dashboard -> Keys -> Add key. 3) Paste into FAL_API_KEY.",
     "FAL_API_KEY",
     "Cheapest way to get many model families behind one key. Runway/Higgsfield are higher-quality, higher-cost alternatives."),

    ("P3", "Creative Generation", "Runway",
     "AI Video Agent: higher-end video generation",
     "Optional", "Easy", "1 day", "Paid plan for API",
     "Credits", 95,
     "Limited trial", "https://dev.runwayml.com",
     "https://docs.dev.runwayml.com",
     "1) Create a Runway account and request/enable API access on a paid plan. 2) Generate an API key in the dev portal. "
     "3) Paste into RUNWAY_API_KEY.",
     "RUNWAY_API_KEY",
     "Expensive per render — gate it behind the Creative Testing Agent so you only render winners' variants."),

    ("P3", "Creative Generation", "Higgsfield",
     "AI Video Agent (as named in the spec)",
     "Optional", "Medium", "Varies", "Account + API availability",
     "Credits", 50,
     "Varies", "https://higgsfield.ai",
     "https://higgsfield.ai",
     "1) Create an account. 2) Check current API availability/waitlist — programmatic access is not always self-serve. "
     "3) If granted, paste the key into HIGGSFIELD_API_KEY.",
     "HIGGSFIELD_API_KEY",
     "Named in the product spec, but API availability shifts. fal.ai or Runway are the practical substitutes today."),

    ("P3", "Organic Social", "YouTube Data API",
     "Social Media Agent + Video Agent: upload and analytics",
     "Optional", "Medium", "2-7 days (quota audit)", "YouTube channel + Google Cloud project",
     "Free within quota", 0,
     "10,000 units/day free", "https://console.cloud.google.com",
     "https://developers.google.com/youtube/v3",
     "1) Enable the 'YouTube Data API v3' in your Google Cloud project. 2) Configure OAuth consent + create an OAuth client. "
     "3) Consent with the youtube.upload scope and capture the refresh token. 4) Fill YOUTUBE_CLIENT_ID/SECRET/REFRESH_TOKEN "
     "and YOUTUBE_CHANNEL_ID. 5) If you need more than ~6 uploads/day, submit a quota-increase audit.",
     "YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN, YOUTUBE_CHANNEL_ID",
     "A single video upload costs ~1,600 quota units against a 10,000/day default — that's ~6 uploads/day before you "
     "need the audit. Plan ahead if video is core."),

    ("P3", "Organic Social", "Ayrshare",
     "Social Media Agent: one key to publish across LinkedIn/IG/FB/X/TikTok",
     "Alternative", "Easy", "1 day", "Connected social accounts",
     "Monthly per profile", 49,
     "Free dev tier", "https://www.ayrshare.com",
     "https://www.ayrshare.com/docs",
     "1) Sign up. 2) Connect each social account through their dashboard. 3) Copy the API key. 4) Paste into AYRSHARE_API_KEY.",
     "AYRSHARE_API_KEY",
     "SHORTCUT: replaces separate Meta/LinkedIn/TikTok/X publishing approvals for ORGANIC posting only. "
     "Ads still need the native APIs. Worth it if platform reviews are blocking you."),

    ("P3", "Paid Media", "TikTok Ads",
     "Paid Media Agent: TikTok campaigns and Spark Ads",
     "Optional", "Hard", "1-3 weeks", "TikTok Business Centre + advertiser account",
     "Ad spend; API free", 0,
     "API free", "https://business-api.tiktok.com",
     "https://business-api.tiktok.com/portal/docs",
     "1) Create a TikTok Business Centre and an advertiser account with billing. "
     "2) business-api.tiktok.com -> Developer -> Create App -> request Marketing API access (describe the use case). "
     "3) After approval, run the OAuth flow to authorise your advertiser account and capture the access token. "
     "4) Fill TIKTOK_APP_ID, TIKTOK_APP_SECRET, TIKTOK_ACCESS_TOKEN, TIKTOK_ADVERTISER_ID.",
     "TIKTOK_APP_ID, TIKTOK_APP_SECRET, TIKTOK_ACCESS_TOKEN, TIKTOK_ADVERTISER_ID",
     "Skip entirely for enterprise B2B. Content Posting API is a SEPARATE app/approval from Ads."),

    ("P3", "WhatsApp / SMS", "WhatsApp Business Cloud API",
     "Lifecycle Agent + AI SDR: WhatsApp conversations and templates",
     "Optional", "Hard", "1-3 weeks", "Verified Meta Business + dedicated phone number",
     "Per-conversation pricing", 50,
     "Free tier of conversations", "https://developers.facebook.com",
     "https://developers.facebook.com/docs/whatsapp/cloud-api",
     "1) Complete Meta Business Verification first (see the Meta Ads row). "
     "2) In your Meta app, add the 'WhatsApp' product. 3) Add a phone number NOT already registered on WhatsApp. "
     "4) Submit your display name for approval. 5) Create and submit message templates for approval (24-48h each). "
     "6) Generate a permanent System User token with whatsapp_business_messaging + whatsapp_business_management. "
     "7) Fill WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_BUSINESS_ACCOUNT_ID, WHATSAPP_ACCESS_TOKEN, WHATSAPP_WEBHOOK_VERIFY_TOKEN.",
     "WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_BUSINESS_ACCOUNT_ID, WHATSAPP_ACCESS_TOKEN, WHATSAPP_WEBHOOK_VERIFY_TOKEN",
     "Depends on Meta Business Verification — do that once, it unlocks Ads + Ad Library + WhatsApp together. "
     "Every outbound template needs individual approval; plan template copy early."),

    ("P3", "SEO & Research", "DataForSEO",
     "SEO Agent: keyword volumes and SERP at lower cost than SerpApi at volume",
     "Alternative", "Instant", "15 minutes", "None",
     "Pay-as-you-go per call", 50,
     "$1 trial credit", "https://app.dataforseo.com",
     "https://docs.dataforseo.com",
     "1) Sign up. 2) Top up the balance. 3) Copy the API login + password (basic auth, not a bearer token). "
     "4) Fill DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD.",
     "DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD",
     "Uses login+password rather than a key. Cheapest per-SERP at volume; alternative to SerpApi, not a complement."),

    ("P3", "AI Models", "Voyage AI",
     "Marketing Memory + knowledge-graph semantic search (embeddings)",
     "Optional", "Instant", "5 minutes", "None",
     "Per-token", 10,
     "Generous free tokens", "https://dashboard.voyageai.com",
     "https://docs.voyageai.com",
     "1) Sign up. 2) API Keys -> create. 3) Paste into VOYAGE_API_KEY and set EMBEDDINGS_PROVIDER=voyage.",
     "VOYAGE_API_KEY, EMBEDDINGS_PROVIDER",
     "Only needed once Marketing Memory grows past a few hundred insights and you want semantic recall."),

    ("P3", "AI Models", "Pinecone",
     "Vector store for Marketing Memory at scale",
     "Optional", "Easy", "20 minutes", "None",
     "Serverless usage-based", 25,
     "Free starter index", "https://app.pinecone.io",
     "https://docs.pinecone.io",
     "1) Sign up. 2) Create a serverless index (dimension must match your embedding model). 3) API Keys -> copy. "
     "4) Fill PINECONE_API_KEY and PINECONE_INDEX.",
     "PINECONE_API_KEY, PINECONE_INDEX",
     "Postgres + pgvector is a cheaper alternative if you're already running Postgres."),

    ("P3", "Email Marketing", "SendGrid",
     "Email Marketing Agent: higher-volume lifecycle sending",
     "Alternative", "Medium", "1-3 days (sender review)", "Domain + DNS access",
     "Emails/month", 20,
     "Free tier (limited)", "https://app.sendgrid.com/settings/api_keys",
     "https://docs.sendgrid.com",
     "1) Sign up (accounts are reviewed — describe your use case honestly). 2) Authenticate your sending domain via DNS. "
     "3) Settings -> API Keys -> Create (Restricted: Mail Send). 4) Set SENDGRID_API_KEY, ESP_PROVIDER=sendgrid.",
     "SENDGRID_API_KEY, ESP_PROVIDER",
     "New accounts get compliance-reviewed and can be suspended for cold-email-looking traffic. "
     "Pick Resend OR SendGrid, not both."),

    ("P3", "Analytics & Revenue", "PostHog",
     "Analytics + CRO: product events and session replay on landing pages",
     "Optional", "Instant", "15 minutes", "None",
     "Events/month", 0,
     "1M events/mo free", "https://app.posthog.com",
     "https://posthog.com/docs",
     "1) Sign up (choose EU or US cloud). 2) Project Settings -> copy the Project API key. "
     "3) Set POSTHOG_API_KEY and POSTHOG_HOST.",
     "POSTHOG_API_KEY, POSTHOG_HOST",
     "Generous free tier; good CRO companion. Pick one of PostHog / Mixpanel / Segment."),

    ("P3", "Analytics & Revenue", "Shopify",
     "Attribution: e-commerce orders and customers as revenue truth",
     "Optional", "Easy", "30 minutes", "Shopify store admin",
     "Free with store plan", 0,
     "Free with store", "https://admin.shopify.com",
     "https://shopify.dev/docs/api",
     "1) Store admin -> Settings -> Apps and sales channels -> Develop apps -> Create an app. "
     "2) Configure Admin API scopes: read_orders, read_customers, read_products. 3) Install the app -> reveal the Admin API "
     "access token. 4) Fill SHOPIFY_STORE_DOMAIN and SHOPIFY_ADMIN_ACCESS_TOKEN.",
     "SHOPIFY_STORE_DOMAIN, SHOPIFY_ADMIN_ACCESS_TOKEN, SHOPIFY_API_VERSION",
     "Only if you sell e-commerce. B2B SaaS should use Stripe or CRM closed-won instead."),

    ("P3", "Landing Pages & CMS", "WordPress",
     "SEO Agent: publish generated articles to your blog",
     "Optional", "Instant", "10 minutes", "WordPress site admin",
     "Free (self-hosted)", 0,
     "Free", "https://your-site.com/wp-admin",
     "https://developer.wordpress.org/rest-api",
     "1) WP Admin -> Users -> your profile -> Application Passwords -> add a new one -> copy it. "
     "2) Fill WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD. "
     "3) Ensure the REST API isn't blocked by a security plugin.",
     "WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD",
     "Application Passwords need HTTPS. Some security plugins disable the REST API by default."),

    ("P3", "Landing Pages & CMS", "Webflow",
     "Landing Page + SEO Agent: CMS publishing",
     "Alternative", "Easy", "20 minutes", "Webflow site on a paid plan",
     "Site plan", 23,
     "Limited free", "https://webflow.com/dashboard",
     "https://developers.webflow.com",
     "1) Site Settings -> Apps & Integrations -> API access -> generate a token (or create a Webflow App). "
     "2) Copy the Site ID from Site Settings -> General. 3) Fill WEBFLOW_API_TOKEN and WEBFLOW_SITE_ID.",
     "WEBFLOW_API_TOKEN, WEBFLOW_SITE_ID",
     "Alternative to WordPress — pick whichever your marketing site already runs on."),

    ("P3", "Alerts & Ops", "Sentry",
     "Platform: error tracking for agent runs and API failures",
     "Recommended", "Instant", "10 minutes", "None",
     "Errors/month", 0,
     "Free developer tier", "https://sentry.io",
     "https://docs.sentry.io",
     "1) Sign up -> create a Python/Django project. 2) Copy the DSN. 3) Paste into SENTRY_DSN.",
     "SENTRY_DSN",
     "Cheap insurance once agents run unattended on a schedule."),

    # ================================================================= P4 — enterprise / optional
    ("P4", "Prospecting", "ZoomInfo",
     "Waterfall Data Agent: premium enrichment + intent data",
     "Optional", "Enterprise", "2-8 weeks (sales cycle)", "Annual contract, company vetting",
     "Annual contract", 1250,
     "None", "https://www.zoominfo.com",
     "https://api-docs.zoominfo.com",
     "1) Request a demo -> sales qualification call -> negotiate seats + API add-on (API is usually a paid add-on, "
     "not included). 2) Sign the annual contract. 3) Admin portal -> generate API credentials (username/password or "
     "client ID + private key for JWT auth). 4) Fill the ZOOMINFO_* keys.",
     "ZOOMINFO_USERNAME, ZOOMINFO_PASSWORD, ZOOMINFO_CLIENT_ID, ZOOMINFO_PRIVATE_KEY",
     "Expensive and slow — only worth it once Apollo's fill-rate is provably the bottleneck on revenue. "
     "Negotiate the API add-on explicitly; it is often excluded from the base quote."),

    ("P4", "Prospecting", "Clearbit (HubSpot Breeze Intelligence)",
     "Lead Enrichment waterfall step 2",
     "Optional", "Medium", "1-2 weeks", "HubSpot account",
     "Credit packs via HubSpot", 30,
     "Limited free enrichment", "https://clearbit.com",
     "https://developers.hubspot.com",
     "1) Clearbit is now part of HubSpot (Breeze Intelligence) — standalone signup has been folded in. "
     "2) Access enrichment through your HubSpot portal and buy credits there. "
     "3) If you hold a legacy standalone Clearbit key, it still works in CLEARBIT_API_KEY.",
     "CLEARBIT_API_KEY",
     "PRODUCT HAS MOVED — verify the current path before budgeting. People Data Labs is the cleaner "
     "standalone alternative for waterfall step 2."),

    ("P4", "Prospecting", "People Data Labs",
     "Waterfall Data Agent: person/company enrichment fallback",
     "Optional", "Easy", "1 day", "Use-case review on signup",
     "Credits", 100,
     "100 free credits", "https://dashboard.peopledatalabs.com",
     "https://docs.peopledatalabs.com",
     "1) Sign up and describe your use case (they review it). 2) Dashboard -> API Keys -> copy. "
     "3) Paste into PEOPLE_DATA_LABS_API_KEY and add 'peopledatalabs' to ENRICHMENT_WATERFALL.",
     "PEOPLE_DATA_LABS_API_KEY, ENRICHMENT_WATERFALL",
     "Good standalone waterfall step 2 now that Clearbit moved into HubSpot."),

    ("P4", "Prospecting", "Crunchbase",
     "Market Intelligence + Research Agent: funding signals",
     "Optional", "Medium", "1-2 weeks", "Paid plan for API",
     "Annual API licence", 150,
     "None for API", "https://data.crunchbase.com",
     "https://data.crunchbase.com/docs",
     "1) Request API access via the Crunchbase data portal (sales-assisted). 2) Purchase a licence. "
     "3) Copy the user key -> CRUNCHBASE_API_KEY.",
     "CRUNCHBASE_API_KEY",
     "Funding signals are also available free-ish via news search (Tavily/NewsAPI) — try that first."),

    ("P4", "Prospecting", "BuiltWith",
     "ICP Scoring Agent: tech-stack detection for fit scoring",
     "Optional", "Instant", "15 minutes", "None",
     "Monthly API plan", 295,
     "Limited free lookups", "https://api.builtwith.com",
     "https://api.builtwith.com",
     "1) Sign up for an API plan. 2) Copy the key. 3) Paste into BUILTWITH_API_KEY.",
     "BUILTWITH_API_KEY",
     "Pricey for what it is. Apollo/PDL already return partial tech-stack data — check the gap before buying."),

    ("P4", "Prospecting", "Proxycurl",
     "Research Agent: LinkedIn-compatible profile data via official-ish API",
     "Optional", "Instant", "10 minutes", "None",
     "Credits", 49,
     "Trial credits", "https://nubela.co/proxycurl",
     "https://nubela.co/proxycurl/docs",
     "1) Sign up. 2) Buy credits. 3) Copy the key -> PROXYCURL_API_KEY.",
     "PROXYCURL_API_KEY",
     "REVIEW THE LEGAL POSITION for your jurisdiction and target geos before using third-party LinkedIn data. "
     "The spec mandates platform-compliant automation only."),

    ("P4", "CRM", "Salesforce",
     "CRM Agent (enterprise alternative to HubSpot)",
     "Alternative", "Medium", "1-3 days", "Salesforce org + admin rights",
     "Per-seat licence", 165,
     "Developer Edition free", "https://developer.salesforce.com",
     "https://developer.salesforce.com/docs",
     "1) Setup -> App Manager -> New Connected App. 2) Enable OAuth; scopes: api, refresh_token, offline_access. "
     "3) Copy the Consumer Key/Secret. 4) Get your security token (Personal Settings -> Reset Security Token, emailed). "
     "5) Fill the SALESFORCE_* keys and set CRM_PROVIDER=salesforce.",
     "SALESFORCE_CLIENT_ID, SALESFORCE_CLIENT_SECRET, SALESFORCE_USERNAME, SALESFORCE_PASSWORD, "
     "SALESFORCE_SECURITY_TOKEN, SALESFORCE_INSTANCE_URL, CRM_PROVIDER",
     "Use a free Developer Edition org to build against before touching production. Pick ONE CRM."),

    ("P4", "CRM", "Pipedrive",
     "CRM Agent (SMB alternative)",
     "Alternative", "Instant", "10 minutes", "Pipedrive account",
     "Per-seat", 24,
     "Trial only", "https://app.pipedrive.com/settings/api",
     "https://developers.pipedrive.com",
     "1) Personal preferences -> API -> copy your personal API token. "
     "2) Fill PIPEDRIVE_API_TOKEN, PIPEDRIVE_COMPANY_DOMAIN, CRM_PROVIDER=pipedrive.",
     "PIPEDRIVE_API_TOKEN, PIPEDRIVE_COMPANY_DOMAIN, CRM_PROVIDER",
     "Simplest CRM API of the three. Pick ONE CRM."),

    ("P4", "Outbound Sending", "Microsoft Graph",
     "Reply Intelligence + AI SDR for Microsoft 365 shops",
     "Alternative", "Medium", "1-3 days", "Microsoft 365 tenant + admin consent",
     "Free with M365", 0,
     "Free with M365", "https://portal.azure.com",
     "https://learn.microsoft.com/graph",
     "1) Entra ID (Azure AD) -> App registrations -> New registration. "
     "2) API permissions -> Microsoft Graph -> Mail.Read, Mail.Send, Calendars.ReadWrite -> Grant admin consent. "
     "3) Certificates & secrets -> New client secret -> copy the VALUE (not the ID). "
     "4) Fill MS_GRAPH_TENANT_ID, MS_GRAPH_CLIENT_ID, MS_GRAPH_CLIENT_SECRET.",
     "MS_GRAPH_TENANT_ID, MS_GRAPH_CLIENT_ID, MS_GRAPH_CLIENT_SECRET",
     "Needs a tenant admin to grant consent — book that person's time early. Alternative to Gmail, not a complement."),

    ("P4", "Outbound Sending", "Smartlead",
     "AI Sequence Agent (alternative to Instantly)",
     "Alternative", "Easy", "1 day + warmup", "Sending domains + mailboxes",
     "Monthly per seat", 39,
     "Trial", "https://app.smartlead.ai",
     "https://api.smartlead.ai/reference",
     "1) Sign up, connect mailboxes, enable warmup. 2) Settings -> API -> copy key. "
     "3) Set SMARTLEAD_API_KEY and OUTBOUND_PROVIDER=smartlead.",
     "SMARTLEAD_API_KEY, OUTBOUND_PROVIDER",
     "Pick ONE sending platform. Same domain/warmup prerequisites as Instantly."),

    ("P4", "Outbound Sending", "lemlist",
     "AI Sequence Agent with native LinkedIn steps",
     "Alternative", "Easy", "1 day + warmup", "Sending domains + mailboxes",
     "Monthly per seat", 69,
     "Trial", "https://app.lemlist.com",
     "https://developer.lemlist.com",
     "1) Sign up, connect mailboxes, enable warmup. 2) Settings -> Integrations -> API -> copy key. "
     "3) Set LEMLIST_API_KEY and OUTBOUND_PROVIDER=lemlist.",
     "LEMLIST_API_KEY, OUTBOUND_PROVIDER",
     "Its LinkedIn steps are the differentiator if the LinkedIn API approval stalls. Pick ONE sending platform."),

    ("P4", "Outbound Sending", "Calendly",
     "AI SDR meeting booking (alternative to Cal.com)",
     "Alternative", "Instant", "10 minutes", "Paid plan for API",
     "Per-seat", 12,
     "Free tier lacks API", "https://calendly.com/integrations/api_webhooks",
     "https://developer.calendly.com",
     "1) Upgrade to a paid plan. 2) Integrations -> API & Webhooks -> generate a personal access token. "
     "3) Paste into CALENDLY_API_KEY.",
     "CALENDLY_API_KEY",
     "API requires a paid tier; Cal.com's free tier includes API access."),

    ("P4", "Email Marketing", "Klaviyo",
     "Lifecycle Agent (e-commerce-oriented flows)",
     "Alternative", "Instant", "15 minutes", "Klaviyo account",
     "By profile count", 45,
     "Free to 250 profiles", "https://www.klaviyo.com",
     "https://developers.klaviyo.com",
     "1) Sign up. 2) Settings -> API Keys -> create a Private API key with the scopes you need. "
     "3) Paste into KLAVIYO_API_KEY and set ESP_PROVIDER=klaviyo.",
     "KLAVIYO_API_KEY, ESP_PROVIDER",
     "Best for e-commerce lifecycle. Pick ONE ESP."),

    ("P4", "Email Marketing", "Mailchimp",
     "Email Marketing Agent (newsletter-oriented)",
     "Alternative", "Instant", "10 minutes", "Mailchimp account",
     "By contact count", 20,
     "Free to 500 contacts", "https://mailchimp.com",
     "https://mailchimp.com/developer",
     "1) Sign up. 2) Account -> Extras -> API keys -> create. 3) Note the server prefix (the 'us21' in your dashboard URL). "
     "4) Fill MAILCHIMP_API_KEY, MAILCHIMP_SERVER_PREFIX, ESP_PROVIDER=mailchimp.",
     "MAILCHIMP_API_KEY, MAILCHIMP_SERVER_PREFIX, ESP_PROVIDER",
     "The server prefix is required and easy to miss. Pick ONE ESP."),

    ("P4", "Email Marketing", "Brevo",
     "Email Marketing + SMS (cheap alternative)",
     "Alternative", "Instant", "10 minutes", "Brevo account",
     "Emails/day or month", 25,
     "300 emails/day free", "https://app.brevo.com",
     "https://developers.brevo.com",
     "1) Sign up. 2) SMTP & API -> API Keys -> generate. 3) Paste into BREVO_API_KEY, set ESP_PROVIDER=brevo.",
     "BREVO_API_KEY, ESP_PROVIDER",
     "Cheapest of the ESPs at low volume. Pick ONE ESP."),

    ("P4", "WhatsApp / SMS", "Twilio",
     "Lifecycle Agent: SMS fallback",
     "Optional", "Instant", "1 day (number purchase)", "Card + number purchase",
     "Per-message + number rental", 20,
     "Trial credit", "https://console.twilio.com",
     "https://www.twilio.com/docs",
     "1) Sign up. 2) Buy a phone number with SMS capability. 3) Console dashboard -> copy Account SID + Auth Token. "
     "4) Fill TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER.",
     "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER",
     "A2P 10DLC registration is required for US SMS and takes extra days. Check per-country SMS regulations."),

    ("P4", "Paid Media", "X (Twitter) Ads",
     "Paid Media Agent: X campaigns",
     "Optional", "Hard", "2-6 weeks", "Paid API tier + Ads account",
     "API subscription + ad spend", 200,
     "None meaningful", "https://developer.x.com",
     "https://developer.x.com/en/docs/x-ads-api",
     "1) Subscribe to a paid X API tier. 2) Create a project + app. 3) Apply separately for Ads API access with a "
     "business justification. 4) Generate consumer keys and access tokens. 5) Fill the X_* keys.",
     "X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET, X_ADS_ACCOUNT_ID",
     "Poor cost/benefit for most B2B. Lowest priority of all the paid channels."),

    ("P4", "Organic Social", "TikTok Content Posting",
     "Social Media Agent: organic TikTok publishing",
     "Optional", "Hard", "1-3 weeks", "TikTok developer app",
     "Free", 0,
     "Free", "https://developers.tiktok.com",
     "https://developers.tiktok.com/doc/content-posting-api-get-started",
     "1) developers.tiktok.com -> create an app. 2) Add the 'Content Posting API' product and apply (separate from Ads). "
     "3) Complete the URL-ownership verification. 4) Fill TIKTOK_CONTENT_CLIENT_KEY and TIKTOK_CONTENT_CLIENT_SECRET.",
     "TIKTOK_CONTENT_CLIENT_KEY, TIKTOK_CONTENT_CLIENT_SECRET",
     "A DIFFERENT app and approval from TikTok Ads. Ayrshare is the shortcut if you just want to publish."),

    ("P4", "SEO & Research", "Semrush",
     "SEO + Competitor Intelligence: keyword and competitor data",
     "Optional", "Medium", "1 day", "Business plan for API",
     "API units on Business plan", 500,
     "None for API", "https://www.semrush.com/api-documentation/",
     "https://developer.semrush.com",
     "1) Subscribe to the Business plan (API access is gated to it). 2) Profile -> Subscription info -> API units -> copy key. "
     "3) Paste into SEMRUSH_API_KEY.",
     "SEMRUSH_API_KEY",
     "Expensive — the API sits behind the top tier. SerpApi + Search Console cover most of the need for far less."),

    ("P4", "SEO & Research", "Ahrefs",
     "SEO Agent: backlinks and keyword difficulty",
     "Optional", "Medium", "1 day", "Enterprise/API plan",
     "API add-on", 500,
     "None for API", "https://ahrefs.com/api",
     "https://ahrefs.com/api/documentation",
     "1) Subscribe to a plan with API access. 2) Account -> API -> generate token. 3) Paste into AHREFS_API_KEY.",
     "AHREFS_API_KEY",
     "Same story as Semrush — high cost, late priority. Pick at most one SEO suite."),

    ("P4", "SEO & Research", "Exa",
     "AI Research Agent: neural/semantic web search",
     "Alternative", "Instant", "5 minutes", "None",
     "Per-search", 25,
     "Free credits", "https://dashboard.exa.ai",
     "https://docs.exa.ai",
     "1) Sign up. 2) Copy the API key. 3) Paste into EXA_API_KEY.",
     "EXA_API_KEY",
     "Alternative to Tavily — you do not need both."),

    ("P4", "SEO & Research", "NewsAPI",
     "Market Intelligence Agent: news monitoring for signals",
     "Optional", "Instant", "5 minutes", "None",
     "Requests/day", 0,
     "Free for dev (non-commercial)", "https://newsapi.org",
     "https://newsapi.org/docs",
     "1) Register. 2) Copy the API key. 3) Paste into NEWSAPI_KEY.",
     "NEWSAPI_KEY",
     "The free tier is development-only and delayed — you must upgrade for production/commercial use."),

    ("P4", "Analytics & Revenue", "Segment",
     "Analytics Agent: unified event pipeline",
     "Optional", "Easy", "1 day", "Segment workspace",
     "By monthly tracked users", 120,
     "Free to 1,000 MTUs", "https://app.segment.com",
     "https://segment.com/docs",
     "1) Create a workspace -> add a Source (Node/HTTP API). 2) Copy the Write Key. 3) Paste into SEGMENT_WRITE_KEY.",
     "SEGMENT_WRITE_KEY",
     "Only worth it if you already have multiple destinations to fan out to. PostHog is cheaper for one tool."),

    ("P4", "Analytics & Revenue", "Mixpanel",
     "Analytics Agent: product analytics",
     "Alternative", "Instant", "15 minutes", "None",
     "By monthly events", 0,
     "Generous free tier", "https://mixpanel.com",
     "https://developer.mixpanel.com",
     "1) Sign up -> create a project. 2) Project Settings -> copy the Project Token. 3) Paste into MIXPANEL_PROJECT_TOKEN.",
     "MIXPANEL_PROJECT_TOKEN",
     "Pick one of PostHog / Mixpanel / Segment."),

    ("P4", "Landing Pages & CMS", "VWO",
     "CRO Agent: A/B testing engine on landing pages",
     "Optional", "Medium", "1-3 days", "Paid plan",
     "By tested visitors", 200,
     "Trial", "https://app.vwo.com",
     "https://developers.vwo.com",
     "1) Subscribe. 2) Settings -> API -> generate a token. 3) Fill VWO_ACCOUNT_ID and VWO_API_TOKEN.",
     "VWO_ACCOUNT_ID, VWO_API_TOKEN",
     "The CRO Agent can run experiments natively on generated pages — only buy VWO for pages you don't control."),

    ("P4", "AI Models", "Anthropic (Claude)",
     "Alternative LLM for every agent (set LLM_PROVIDER=anthropic)",
     "Alternative", "Instant", "5 minutes", "Email + card",
     "Prepaid credits, per-token", 150,
     "$5 trial credit", "https://console.anthropic.com/settings/keys",
     "https://docs.anthropic.com",
     "1) pip install anthropic. 2) Sign up at console.anthropic.com, add a payment method and buy credits. "
     "3) API Keys -> Create Key -> copy once. 4) Set ANTHROPIC_API_KEY and LLM_PROVIDER=anthropic. "
     "5) Set a monthly spend limit under Billing -> Limits.",
     "ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ANTHROPIC_WORKER_MODEL, LLM_PROVIDER",
     "Stronger reasoning than the Groq models but roughly 5-10x the cost and much slower per response. "
     "Worth testing if agent output quality is the bottleneck. Pick ONE LLM provider."),

    ("P4", "AI Models", "OpenAI",
     "Alternative LLM / embeddings (set LLM_PROVIDER=openai)",
     "Alternative", "Instant", "5 minutes", "Card",
     "Per-token", 20,
     "None (prepaid)", "https://platform.openai.com/api-keys",
     "https://platform.openai.com/docs",
     "1) pip install openai. 2) Sign up -> Billing -> add credits. 3) API Keys -> create. "
     "4) Set OPENAI_API_KEY and LLM_PROVIDER=openai. OPENAI_BASE_URL also lets you point at any "
     "OpenAI-compatible gateway (Together, OpenRouter, a local vLLM server).",
     "OPENAI_API_KEY, OPENAI_MODEL, OPENAI_WORKER_MODEL, OPENAI_BASE_URL, LLM_PROVIDER",
     "Not required - the agents run on Groq by default. Pick ONE LLM provider."),

    ("P4", "Creative Generation", "Stability AI",
     "Creative Director: image generation",
     "Optional", "Instant", "5 minutes", "None",
     "Credits", 20,
     "Trial credits", "https://platform.stability.ai",
     "https://platform.stability.ai/docs",
     "1) Sign up. 2) Account -> API Keys -> copy. 3) Paste into STABILITY_API_KEY.",
     "STABILITY_API_KEY",
     "fal.ai gives you this plus more models behind one key."),

    ("P4", "Storage", "AWS S3 / Cloudflare R2",
     "Storage for generated creatives, videos and exports",
     "Optional", "Easy", "30 minutes", "AWS or Cloudflare account",
     "Per GB stored + egress", 5,
     "R2 has free egress", "https://aws.amazon.com/s3/",
     "https://docs.aws.amazon.com/s3/",
     "1) Create a bucket (private). 2) Create an IAM user with least-privilege access to that bucket only. "
     "3) Generate an access key pair. 4) Fill AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, "
     "AWS_S3_REGION_NAME and set STORAGE_BACKEND=s3.",
     "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME, STORAGE_BACKEND",
     "Local storage is the default and fine until you generate video at volume. R2 avoids egress fees."),
]


# ---------------------------------------------------------------- prerequisites (non-API blockers)
# (item, why it blocks, owner hint, lead time, how to do it)
PREREQS: list[tuple] = [
    ("Legal business entity + registration document",
     "Meta Business Verification, Google Ads billing, ZoomInfo/Semrush contracts, Stripe live mode all require it",
     "Founder / Finance", "Already done, or weeks",
     "Have the incorporation certificate, tax ID and a document showing the business address ready as PDFs before you start any verification."),

    ("Company domain with DNS access",
     "Domain authentication for every email provider, GSC verification, landing-page subdomains",
     "Founder / IT", "Same day",
     "Make sure you (not an agency) can add TXT/CNAME records. Check now, not on the day you need it."),

    ("2-3 SECONDARY sending domains + mailboxes",
     "Cold outbound must never run on your primary domain — a spam trap can kill your real email",
     "Growth", "1 day to buy, 2-3 WEEKS to warm",
     "Buy lookalike domains (get-acme.com, tryacme.com, acme-hq.com). Create 2-3 mailboxes each in Google Workspace or "
     "M365. Set SPF, DKIM and DMARC on all of them. Connect to Instantly and turn warmup on. START THIS FIRST — "
     "it is the longest-lead item in the whole project."),

    ("Google Ads Manager (MCC) account",
     "Required before you can even apply for a developer token",
     "Growth", "1 hour",
     "Create at ads.google.com/home/tools/manager-accounts, then link your ad account to it."),

    ("Meta Business Account + Page + Ad Account + Instagram",
     "Everything Meta (Ads, Ad Library, WhatsApp) hangs off this",
     "Growth", "1 day + verification wait",
     "Set up at business.facebook.com, then immediately start Business Verification in Security Centre."),

    ("LinkedIn Company Page with admin rights",
     "Required to create and verify a LinkedIn developer app",
     "Founder", "1 day",
     "You must be a Page admin. Page verification inside the developer app needs an admin to click a link."),

    ("Google Cloud project + service account",
     "Shared by GA4, Search Console, Gmail, YouTube and Google Ads OAuth",
     "Engineering", "1 hour",
     "Create ONE project and reuse it. Download the service-account JSON, store it outside git, "
     "reference it via GOOGLE_SERVICE_ACCOUNT_JSON_PATH."),

    ("Privacy policy + terms + cookie consent on your site",
     "App reviews (Meta, Google, LinkedIn, TikTok) check for these; GDPR requires them",
     "Founder / Legal", "2-3 days",
     "Publish them at stable URLs before you submit any app review — reviewers do check."),

    ("Outbound compliance position for your target geos",
     "GDPR (EU), CAN-SPAM (US), CASL (Canada), PECR (UK) all constrain cold outbound differently",
     "Founder / Legal", "1 week",
     "Decide your legal basis per geography, add a working unsubscribe to every sequence, keep a suppression list, "
     "and honour opt-outs immediately. The Lead Verification + Compliance agents enforce this only if you configure it."),

    ("CREDENTIALS_ENCRYPTION_KEY generated",
     "Connector credentials saved in the UI are stored in plaintext without it",
     "Engineering", "1 minute",
     "Run: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\" "
     "and put the result in CREDENTIALS_ENCRYPTION_KEY. Do this BEFORE saving any key in the Integrations screen."),

    ("Spend guardrails agreed",
     "Full-autonomy mode can spend real money on real ad platforms",
     "Founder", "30 minutes",
     "Set DEFAULT_DAILY_SPEND_CAP and the per-agent modes in Settings -> Control & guardrails BEFORE connecting any "
     "ad platform. Keep AI_CAN_LAUNCH_PAID_WITHOUT_APPROVAL off until you trust the output."),
]
