"""
Provider registry for the connector framework (spec section 8).

Each capability sits behind an internal interface with multiple provider adapters.
`env_vars` lists the .env keys that make a provider "configured" without the UI.
"""
from __future__ import annotations

import os

CATEGORIES = {
    "ai": "AI Models",
    "paid_media": "Paid Media",
    "social": "Organic Social",
    "prospecting": "Prospecting & Enrichment",
    "verification": "Email Verification",
    "outbound": "Outbound Sending",
    "email": "Email Marketing / Lifecycle",
    "messaging": "WhatsApp / SMS",
    "crm": "CRM",
    "analytics": "Analytics & Revenue",
    "seo": "SEO & Research",
    "creative": "Creative Generation",
    "web": "Landing Pages & CMS",
    "alerts": "Alerts & Ops",
}

PROVIDERS: list[dict] = [
    # AI
    {"key": "groq", "name": "Groq", "category": "ai", "env_vars": ["GROQ_API_KEY"], "fields": ["api_key"], "docs": "https://console.groq.com/docs", "capabilities": ["reasoning", "generation", "classification"], "used_by": ["cmo", "all agents"]},
    {"key": "anthropic", "name": "Anthropic Claude", "category": "ai", "env_vars": ["ANTHROPIC_API_KEY"], "fields": ["api_key"], "docs": "https://docs.anthropic.com", "capabilities": ["reasoning", "generation", "classification"], "used_by": ["alternative to Groq"]},
    {"key": "openai", "name": "OpenAI", "category": "ai", "env_vars": ["OPENAI_API_KEY"], "fields": ["api_key"], "docs": "https://platform.openai.com/docs", "capabilities": ["reasoning", "embeddings"], "used_by": ["alternative to Groq", "memory"]},
    {"key": "voyage", "name": "Voyage AI", "category": "ai", "env_vars": ["VOYAGE_API_KEY"], "fields": ["api_key"], "docs": "https://docs.voyageai.com", "capabilities": ["embeddings"], "used_by": ["memory", "business_intelligence"]},
    {"key": "pinecone", "name": "Pinecone", "category": "ai", "env_vars": ["PINECONE_API_KEY"], "fields": ["api_key", "index"], "docs": "https://docs.pinecone.io", "capabilities": ["vector_store"], "used_by": ["memory"]},
    # Paid media
    {"key": "meta_ads", "name": "Meta Ads", "category": "paid_media", "env_vars": ["META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID"], "fields": ["access_token", "ad_account_id", "pixel_id", "page_id"], "docs": "https://developers.facebook.com/docs/marketing-apis", "capabilities": ["campaigns", "creatives", "audiences", "insights", "ad_library"], "used_by": ["paid_media", "media_buyer", "competitor_intelligence"]},
    {"key": "google_ads", "name": "Google Ads", "category": "paid_media", "env_vars": ["GOOGLE_ADS_DEVELOPER_TOKEN", "GOOGLE_ADS_REFRESH_TOKEN", "GOOGLE_ADS_CUSTOMER_ID"], "fields": ["developer_token", "client_id", "client_secret", "refresh_token", "customer_id", "login_customer_id"], "docs": "https://developers.google.com/google-ads/api", "capabilities": ["search", "display", "youtube", "conversions"], "used_by": ["paid_media", "media_buyer"]},
    {"key": "linkedin_ads", "name": "LinkedIn Marketing", "category": "paid_media", "env_vars": ["LINKEDIN_ACCESS_TOKEN", "LINKEDIN_AD_ACCOUNT_ID"], "fields": ["access_token", "ad_account_id", "organization_id"], "docs": "https://learn.microsoft.com/linkedin/marketing", "capabilities": ["campaigns", "lead_gen_forms", "organic_posts"], "used_by": ["paid_media", "linkedin"]},
    {"key": "tiktok_ads", "name": "TikTok Ads", "category": "paid_media", "env_vars": ["TIKTOK_ACCESS_TOKEN", "TIKTOK_ADVERTISER_ID"], "fields": ["access_token", "advertiser_id"], "docs": "https://business-api.tiktok.com/portal/docs", "capabilities": ["campaigns", "spark_ads"], "used_by": ["paid_media"]},
    {"key": "x_ads", "name": "X Ads", "category": "paid_media", "env_vars": ["X_API_KEY", "X_ADS_ACCOUNT_ID"], "fields": ["api_key", "api_secret", "access_token", "access_token_secret", "ads_account_id"], "docs": "https://developer.x.com/en/docs/x-ads-api", "capabilities": ["campaigns"], "used_by": ["paid_media"]},
    # Social
    {"key": "youtube", "name": "YouTube", "category": "social", "env_vars": ["YOUTUBE_REFRESH_TOKEN", "YOUTUBE_CHANNEL_ID"], "fields": ["client_id", "client_secret", "refresh_token", "channel_id"], "docs": "https://developers.google.com/youtube/v3", "capabilities": ["upload", "analytics"], "used_by": ["social", "video"]},
    {"key": "tiktok_content", "name": "TikTok Content", "category": "social", "env_vars": ["TIKTOK_CONTENT_CLIENT_KEY"], "fields": ["client_key", "client_secret"], "docs": "https://developers.tiktok.com/doc/content-posting-api-get-started", "capabilities": ["publish"], "used_by": ["social"]},
    {"key": "ayrshare", "name": "Ayrshare (multi-network)", "category": "social", "env_vars": ["AYRSHARE_API_KEY"], "fields": ["api_key"], "docs": "https://www.ayrshare.com/docs", "capabilities": ["publish", "schedule", "analytics"], "used_by": ["social"]},
    # Prospecting
    {"key": "apollo", "name": "Apollo.io", "category": "prospecting", "env_vars": ["APOLLO_API_KEY"], "fields": ["api_key"], "docs": "https://apolloio.github.io/apollo-api-docs", "capabilities": ["search_people", "search_orgs", "enrich"], "used_by": ["lead_discovery", "lead_enrichment"]},
    {"key": "clearbit", "name": "Clearbit", "category": "prospecting", "env_vars": ["CLEARBIT_API_KEY"], "fields": ["api_key"], "docs": "https://clearbit.com/docs", "capabilities": ["enrich"], "used_by": ["lead_enrichment", "waterfall_data"]},
    {"key": "peopledatalabs", "name": "People Data Labs", "category": "prospecting", "env_vars": ["PEOPLE_DATA_LABS_API_KEY"], "fields": ["api_key"], "docs": "https://docs.peopledatalabs.com", "capabilities": ["enrich", "search"], "used_by": ["waterfall_data"]},
    {"key": "hunter", "name": "Hunter.io", "category": "prospecting", "env_vars": ["HUNTER_API_KEY"], "fields": ["api_key"], "docs": "https://hunter.io/api-documentation", "capabilities": ["email_finder"], "used_by": ["waterfall_data"]},
    {"key": "zoominfo", "name": "ZoomInfo", "category": "prospecting", "env_vars": ["ZOOMINFO_USERNAME", "ZOOMINFO_PASSWORD"], "fields": ["username", "password", "client_id", "private_key"], "docs": "https://api-docs.zoominfo.com", "capabilities": ["enrich", "intent"], "used_by": ["waterfall_data"]},
    {"key": "crunchbase", "name": "Crunchbase", "category": "prospecting", "env_vars": ["CRUNCHBASE_API_KEY"], "fields": ["api_key"], "docs": "https://data.crunchbase.com/docs", "capabilities": ["funding_signals"], "used_by": ["market_intelligence", "research"]},
    {"key": "builtwith", "name": "BuiltWith", "category": "prospecting", "env_vars": ["BUILTWITH_API_KEY"], "fields": ["api_key"], "docs": "https://api.builtwith.com", "capabilities": ["tech_stack"], "used_by": ["icp_scoring"]},
    # Verification
    {"key": "zerobounce", "name": "ZeroBounce", "category": "verification", "env_vars": ["ZEROBOUNCE_API_KEY"], "fields": ["api_key"], "docs": "https://www.zerobounce.net/docs", "capabilities": ["verify_email"], "used_by": ["lead_verification"]},
    {"key": "neverbounce", "name": "NeverBounce", "category": "verification", "env_vars": ["NEVERBOUNCE_API_KEY"], "fields": ["api_key"], "docs": "https://developers.neverbounce.com", "capabilities": ["verify_email"], "used_by": ["lead_verification"]},
    {"key": "millionverifier", "name": "MillionVerifier", "category": "verification", "env_vars": ["MILLIONVERIFIER_API_KEY"], "fields": ["api_key"], "docs": "https://developer.millionverifier.com", "capabilities": ["verify_email"], "used_by": ["lead_verification"]},
    # Outbound
    {"key": "instantly", "name": "Instantly", "category": "outbound", "env_vars": ["INSTANTLY_API_KEY"], "fields": ["api_key"], "docs": "https://developer.instantly.ai", "capabilities": ["campaigns", "mailboxes", "warmup", "replies"], "used_by": ["sequence", "reply_intelligence"]},
    {"key": "smartlead", "name": "Smartlead", "category": "outbound", "env_vars": ["SMARTLEAD_API_KEY"], "fields": ["api_key"], "docs": "https://api.smartlead.ai/reference", "capabilities": ["campaigns", "mailboxes"], "used_by": ["sequence"]},
    {"key": "lemlist", "name": "lemlist", "category": "outbound", "env_vars": ["LEMLIST_API_KEY"], "fields": ["api_key"], "docs": "https://developer.lemlist.com", "capabilities": ["campaigns", "linkedin_steps"], "used_by": ["sequence"]},
    {"key": "gmail", "name": "Gmail", "category": "outbound", "env_vars": ["GMAIL_REFRESH_TOKEN"], "fields": ["client_id", "client_secret", "refresh_token"], "docs": "https://developers.google.com/gmail/api", "capabilities": ["send", "read_replies"], "used_by": ["sdr", "reply_intelligence"]},
    {"key": "microsoft_graph", "name": "Outlook / Microsoft 365", "category": "outbound", "env_vars": ["MS_GRAPH_CLIENT_ID", "MS_GRAPH_CLIENT_SECRET"], "fields": ["tenant_id", "client_id", "client_secret"], "docs": "https://learn.microsoft.com/graph", "capabilities": ["send", "read_replies", "calendar"], "used_by": ["sdr"]},
    {"key": "calendly", "name": "Calendly", "category": "outbound", "env_vars": ["CALENDLY_API_KEY"], "fields": ["api_key"], "docs": "https://developer.calendly.com", "capabilities": ["booking"], "used_by": ["sdr"]},
    {"key": "cal_com", "name": "Cal.com", "category": "outbound", "env_vars": ["CAL_COM_API_KEY"], "fields": ["api_key"], "docs": "https://cal.com/docs/api-reference", "capabilities": ["booking"], "used_by": ["sdr"]},
    # Email marketing
    {"key": "sendgrid", "name": "SendGrid", "category": "email", "env_vars": ["SENDGRID_API_KEY"], "fields": ["api_key"], "docs": "https://docs.sendgrid.com", "capabilities": ["send", "lists", "stats"], "used_by": ["email_marketing", "lifecycle"]},
    {"key": "resend", "name": "Resend", "category": "email", "env_vars": ["RESEND_API_KEY"], "fields": ["api_key"], "docs": "https://resend.com/docs", "capabilities": ["send"], "used_by": ["email_marketing"]},
    {"key": "klaviyo", "name": "Klaviyo", "category": "email", "env_vars": ["KLAVIYO_API_KEY"], "fields": ["api_key"], "docs": "https://developers.klaviyo.com", "capabilities": ["flows", "segments"], "used_by": ["lifecycle"]},
    {"key": "mailchimp", "name": "Mailchimp", "category": "email", "env_vars": ["MAILCHIMP_API_KEY"], "fields": ["api_key", "server_prefix"], "docs": "https://mailchimp.com/developer", "capabilities": ["campaigns", "audiences"], "used_by": ["email_marketing"]},
    {"key": "brevo", "name": "Brevo", "category": "email", "env_vars": ["BREVO_API_KEY"], "fields": ["api_key"], "docs": "https://developers.brevo.com", "capabilities": ["campaigns", "sms"], "used_by": ["email_marketing"]},
    # Messaging
    {"key": "whatsapp", "name": "WhatsApp Business", "category": "messaging", "env_vars": ["WHATSAPP_ACCESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID"], "fields": ["access_token", "phone_number_id", "business_account_id"], "docs": "https://developers.facebook.com/docs/whatsapp/cloud-api", "capabilities": ["templates", "conversations"], "used_by": ["lifecycle", "sdr"]},
    {"key": "twilio", "name": "Twilio", "category": "messaging", "env_vars": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"], "fields": ["account_sid", "auth_token", "from_number"], "docs": "https://www.twilio.com/docs", "capabilities": ["sms"], "used_by": ["lifecycle"]},
    # CRM
    {"key": "hubspot", "name": "HubSpot", "category": "crm", "env_vars": ["HUBSPOT_ACCESS_TOKEN"], "fields": ["access_token", "portal_id"], "docs": "https://developers.hubspot.com/docs/api/overview", "capabilities": ["contacts", "companies", "deals", "notes", "tasks"], "used_by": ["crm", "attribution"]},
    {"key": "salesforce", "name": "Salesforce", "category": "crm", "env_vars": ["SALESFORCE_CLIENT_ID", "SALESFORCE_USERNAME"], "fields": ["client_id", "client_secret", "username", "password", "security_token", "instance_url"], "docs": "https://developer.salesforce.com/docs", "capabilities": ["leads", "opportunities", "accounts"], "used_by": ["crm"]},
    {"key": "pipedrive", "name": "Pipedrive", "category": "crm", "env_vars": ["PIPEDRIVE_API_TOKEN"], "fields": ["api_token", "company_domain"], "docs": "https://developers.pipedrive.com", "capabilities": ["persons", "deals"], "used_by": ["crm"]},
    # Analytics
    {"key": "ga4", "name": "Google Analytics 4", "category": "analytics", "env_vars": ["GA4_PROPERTY_ID"], "fields": ["property_id", "service_account_json"], "docs": "https://developers.google.com/analytics/devguides/reporting/data/v1", "capabilities": ["traffic", "conversions"], "used_by": ["analytics", "cro"]},
    {"key": "search_console", "name": "Google Search Console", "category": "analytics", "env_vars": ["GSC_SITE_URL"], "fields": ["site_url", "service_account_json"], "docs": "https://developers.google.com/webmaster-tools", "capabilities": ["rankings", "queries"], "used_by": ["seo"]},
    {"key": "stripe", "name": "Stripe", "category": "analytics", "env_vars": ["STRIPE_SECRET_KEY"], "fields": ["secret_key", "webhook_secret"], "docs": "https://stripe.com/docs/api", "capabilities": ["revenue", "subscriptions"], "used_by": ["attribution", "revenue_intelligence"]},
    {"key": "shopify", "name": "Shopify", "category": "analytics", "env_vars": ["SHOPIFY_ADMIN_ACCESS_TOKEN"], "fields": ["store_domain", "admin_access_token"], "docs": "https://shopify.dev/docs/api", "capabilities": ["orders", "customers"], "used_by": ["attribution"]},
    {"key": "segment", "name": "Segment", "category": "analytics", "env_vars": ["SEGMENT_WRITE_KEY"], "fields": ["write_key"], "docs": "https://segment.com/docs", "capabilities": ["events"], "used_by": ["analytics"]},
    {"key": "posthog", "name": "PostHog", "category": "analytics", "env_vars": ["POSTHOG_API_KEY"], "fields": ["api_key", "host"], "docs": "https://posthog.com/docs", "capabilities": ["events", "session_replay"], "used_by": ["analytics", "cro"]},
    {"key": "mixpanel", "name": "Mixpanel", "category": "analytics", "env_vars": ["MIXPANEL_PROJECT_TOKEN"], "fields": ["project_token"], "docs": "https://developer.mixpanel.com", "capabilities": ["events"], "used_by": ["analytics"]},
    # SEO & research
    {"key": "semrush", "name": "Semrush", "category": "seo", "env_vars": ["SEMRUSH_API_KEY"], "fields": ["api_key"], "docs": "https://developer.semrush.com", "capabilities": ["keywords", "competitors"], "used_by": ["seo", "competitor_intelligence"]},
    {"key": "ahrefs", "name": "Ahrefs", "category": "seo", "env_vars": ["AHREFS_API_KEY"], "fields": ["api_key"], "docs": "https://ahrefs.com/api", "capabilities": ["backlinks", "keywords"], "used_by": ["seo"]},
    {"key": "serpapi", "name": "SerpApi", "category": "seo", "env_vars": ["SERPAPI_API_KEY"], "fields": ["api_key"], "docs": "https://serpapi.com/search-api", "capabilities": ["serp_monitoring"], "used_by": ["seo"]},
    {"key": "dataforseo", "name": "DataForSEO", "category": "seo", "env_vars": ["DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD"], "fields": ["login", "password"], "docs": "https://docs.dataforseo.com", "capabilities": ["keywords", "serp"], "used_by": ["seo"]},
    {"key": "firecrawl", "name": "Firecrawl", "category": "seo", "env_vars": ["FIRECRAWL_API_KEY"], "fields": ["api_key"], "docs": "https://docs.firecrawl.dev", "capabilities": ["crawl", "scrape"], "used_by": ["business_intelligence", "competitor_intelligence"]},
    {"key": "tavily", "name": "Tavily", "category": "seo", "env_vars": ["TAVILY_API_KEY"], "fields": ["api_key"], "docs": "https://docs.tavily.com", "capabilities": ["web_search"], "used_by": ["market_intelligence", "research"]},
    {"key": "exa", "name": "Exa", "category": "seo", "env_vars": ["EXA_API_KEY"], "fields": ["api_key"], "docs": "https://docs.exa.ai", "capabilities": ["web_search"], "used_by": ["research"]},
    {"key": "newsapi", "name": "NewsAPI", "category": "seo", "env_vars": ["NEWSAPI_KEY"], "fields": ["api_key"], "docs": "https://newsapi.org/docs", "capabilities": ["news"], "used_by": ["market_intelligence"]},
    # Creative
    {"key": "higgsfield", "name": "Higgsfield", "category": "creative", "env_vars": ["HIGGSFIELD_API_KEY"], "fields": ["api_key"], "docs": "https://higgsfield.ai", "capabilities": ["video"], "used_by": ["video"]},
    {"key": "runway", "name": "Runway", "category": "creative", "env_vars": ["RUNWAY_API_KEY"], "fields": ["api_key"], "docs": "https://docs.dev.runwayml.com", "capabilities": ["video"], "used_by": ["video"]},
    {"key": "elevenlabs", "name": "ElevenLabs", "category": "creative", "env_vars": ["ELEVENLABS_API_KEY"], "fields": ["api_key"], "docs": "https://elevenlabs.io/docs", "capabilities": ["voice"], "used_by": ["video"]},
    {"key": "stability", "name": "Stability AI", "category": "creative", "env_vars": ["STABILITY_API_KEY"], "fields": ["api_key"], "docs": "https://platform.stability.ai/docs", "capabilities": ["image"], "used_by": ["creative_director"]},
    {"key": "fal", "name": "fal.ai", "category": "creative", "env_vars": ["FAL_API_KEY"], "fields": ["api_key"], "docs": "https://fal.ai/docs", "capabilities": ["image", "video"], "used_by": ["creative_director", "video"]},
    # Web
    {"key": "vercel", "name": "Vercel", "category": "web", "env_vars": ["VERCEL_TOKEN"], "fields": ["token", "project_id"], "docs": "https://vercel.com/docs/rest-api", "capabilities": ["deploy_landing_pages"], "used_by": ["landing_page"]},
    {"key": "webflow", "name": "Webflow", "category": "web", "env_vars": ["WEBFLOW_API_TOKEN"], "fields": ["api_token", "site_id"], "docs": "https://developers.webflow.com", "capabilities": ["cms", "pages"], "used_by": ["landing_page", "seo"]},
    {"key": "wordpress", "name": "WordPress", "category": "web", "env_vars": ["WORDPRESS_URL", "WORDPRESS_APP_PASSWORD"], "fields": ["url", "username", "app_password"], "docs": "https://developer.wordpress.org/rest-api", "capabilities": ["publish_articles"], "used_by": ["seo"]},
    {"key": "vwo", "name": "VWO", "category": "web", "env_vars": ["VWO_API_TOKEN"], "fields": ["account_id", "api_token"], "docs": "https://developers.vwo.com", "capabilities": ["ab_tests"], "used_by": ["cro"]},
    # Alerts
    {"key": "slack", "name": "Slack", "category": "alerts", "env_vars": ["SLACK_BOT_TOKEN"], "fields": ["bot_token", "channel"], "docs": "https://api.slack.com", "capabilities": ["alerts", "approvals"], "used_by": ["compliance", "cmo"]},
    {"key": "sentry", "name": "Sentry", "category": "alerts", "env_vars": ["SENTRY_DSN"], "fields": ["dsn"], "docs": "https://docs.sentry.io", "capabilities": ["errors"], "used_by": ["platform"]},
]

PROVIDER_BY_KEY = {p["key"]: p for p in PROVIDERS}


def env_configured(provider: dict) -> bool:
    return all(os.environ.get(v) for v in provider["env_vars"])
