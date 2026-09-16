"""
Concrete adapters. Each `_ping` is the cheapest read-only call that proves the
credential works. Write capabilities (create campaign, send email...) are exposed
as methods that raise NotImplementedError until wired - the agents route around
unconfigured providers via waterfall / simulation.
"""
from __future__ import annotations

from .base import BaseAdapter, HealthResult


class GroqAdapter(BaseAdapter):
    key = "groq"
    env_map = {"api_key": "GROQ_API_KEY"}

    def _ping(self):
        r = self._get("https://api.groq.com/openai/v1/models",
                      headers={"Authorization": f"Bearer {self.creds['api_key']}"})
        if r.status_code != 200:
            return HealthResult(False, f"Groq API {r.status_code}: {r.text[:160]}")
        models = sorted(m["id"] for m in r.json().get("data", []))
        return HealthResult(True, f"Connected · {len(models)} models available", {"models": models[:12]})


class AnthropicAdapter(BaseAdapter):
    key = "anthropic"
    env_map = {"api_key": "ANTHROPIC_API_KEY"}

    def _ping(self):
        import anthropic

        client = anthropic.Anthropic(api_key=self.creds["api_key"])
        models = [m.id for m in client.models.list(limit=5)]
        return HealthResult(True, "Connected", {"models": models})


class OpenAIAdapter(BaseAdapter):
    key = "openai"
    env_map = {"api_key": "OPENAI_API_KEY"}

    def _ping(self):
        r = self._get("https://api.openai.com/v1/models",
                      headers={"Authorization": f"Bearer {self.creds['api_key']}"})
        return HealthResult(r.status_code == 200, "Connected" if r.status_code == 200 else f"HTTP {r.status_code}")


class MetaAdsAdapter(BaseAdapter):
    key = "meta_ads"
    env_map = {"access_token": "META_ACCESS_TOKEN", "ad_account_id": "META_AD_ACCOUNT_ID", "pixel_id": "META_PIXEL_ID", "page_id": "META_PAGE_ID"}
    required = ["access_token", "ad_account_id"]
    base = "https://graph.facebook.com/v21.0"

    def _ping(self):
        r = self._get(f"{self.base}/{self.creds['ad_account_id']}", params={"fields": "name,currency,account_status", "access_token": self.creds["access_token"]})
        data = r.json()
        if "error" in data:
            return HealthResult(False, data["error"].get("message", "Meta API error"))
        return HealthResult(True, f"Connected to {data.get('name')}", data)

    def get_insights(self, date_preset="last_30d"):
        r = self._get(f"{self.base}/{self.creds['ad_account_id']}/insights",
                      params={"fields": "spend,impressions,clicks,actions", "date_preset": date_preset, "access_token": self.creds["access_token"]})
        return r.json()


class GoogleAdsAdapter(BaseAdapter):
    key = "google_ads"
    env_map = {"developer_token": "GOOGLE_ADS_DEVELOPER_TOKEN", "client_id": "GOOGLE_ADS_CLIENT_ID", "client_secret": "GOOGLE_ADS_CLIENT_SECRET",
               "refresh_token": "GOOGLE_ADS_REFRESH_TOKEN", "customer_id": "GOOGLE_ADS_CUSTOMER_ID", "login_customer_id": "GOOGLE_ADS_LOGIN_CUSTOMER_ID"}
    required = ["developer_token", "client_id", "client_secret", "refresh_token", "customer_id"]

    def _ping(self):
        import requests

        r = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": self.creds["client_id"], "client_secret": self.creds["client_secret"],
            "refresh_token": self.creds["refresh_token"], "grant_type": "refresh_token"}, timeout=self.timeout)
        if r.status_code != 200:
            return HealthResult(False, f"OAuth refresh failed: {r.text[:200]}")
        return HealthResult(True, "OAuth token refreshed; developer token present", {"customer_id": self.creds["customer_id"]})


class LinkedInAdapter(BaseAdapter):
    key = "linkedin_ads"
    env_map = {"access_token": "LINKEDIN_ACCESS_TOKEN", "ad_account_id": "LINKEDIN_AD_ACCOUNT_ID", "organization_id": "LINKEDIN_ORGANIZATION_ID"}
    required = ["access_token"]

    def _ping(self):
        r = self._get("https://api.linkedin.com/v2/userinfo", headers={"Authorization": f"Bearer {self.creds['access_token']}"})
        if r.status_code != 200:
            return HealthResult(False, f"LinkedIn API {r.status_code}")
        return HealthResult(True, "Connected", r.json())


class TikTokAdsAdapter(BaseAdapter):
    key = "tiktok_ads"
    env_map = {"access_token": "TIKTOK_ACCESS_TOKEN", "advertiser_id": "TIKTOK_ADVERTISER_ID"}

    def _ping(self):
        r = self._get("https://business-api.tiktok.com/open_api/v1.3/advertiser/info/",
                      params={"advertiser_ids": f'["{self.creds["advertiser_id"]}"]'}, headers={"Access-Token": self.creds["access_token"]})
        data = r.json()
        ok = data.get("code") == 0
        return HealthResult(ok, data.get("message", "ok"), data.get("data", {}))


class ApolloAdapter(BaseAdapter):
    key = "apollo"
    env_map = {"api_key": "APOLLO_API_KEY"}

    def _ping(self):
        r = self._get("https://api.apollo.io/v1/auth/health", headers={"X-Api-Key": self.creds["api_key"]})
        data = r.json() if r.content else {}
        return HealthResult(bool(data.get("is_logged_in")), "Connected" if data.get("is_logged_in") else "Invalid key", data)


class HunterAdapter(BaseAdapter):
    key = "hunter"
    env_map = {"api_key": "HUNTER_API_KEY"}

    def _ping(self):
        r = self._get("https://api.hunter.io/v2/account", params={"api_key": self.creds["api_key"]})
        return HealthResult(r.status_code == 200, "Connected" if r.status_code == 200 else f"HTTP {r.status_code}", r.json().get("data", {}) if r.status_code == 200 else {})


class ZeroBounceAdapter(BaseAdapter):
    key = "zerobounce"
    env_map = {"api_key": "ZEROBOUNCE_API_KEY"}

    def _ping(self):
        r = self._get("https://api.zerobounce.net/v2/getcredits", params={"api_key": self.creds["api_key"]})
        data = r.json()
        credits = data.get("Credits", "-1")
        return HealthResult(str(credits) != "-1", f"Credits: {credits}", data)


class InstantlyAdapter(BaseAdapter):
    key = "instantly"
    env_map = {"api_key": "INSTANTLY_API_KEY"}

    def _ping(self):
        r = self._get("https://api.instantly.ai/api/v2/accounts", params={"limit": 1}, headers={"Authorization": f"Bearer {self.creds['api_key']}"})
        return HealthResult(r.status_code == 200, "Connected" if r.status_code == 200 else f"HTTP {r.status_code}")


class SmartleadAdapter(BaseAdapter):
    key = "smartlead"
    env_map = {"api_key": "SMARTLEAD_API_KEY"}

    def _ping(self):
        r = self._get("https://server.smartlead.ai/api/v1/campaigns", params={"api_key": self.creds["api_key"]})
        return HealthResult(r.status_code == 200, "Connected" if r.status_code == 200 else f"HTTP {r.status_code}")


class HubSpotAdapter(BaseAdapter):
    key = "hubspot"
    env_map = {"access_token": "HUBSPOT_ACCESS_TOKEN", "portal_id": "HUBSPOT_PORTAL_ID"}
    required = ["access_token"]

    def _ping(self):
        r = self._get("https://api.hubapi.com/crm/v3/objects/contacts", params={"limit": 1}, headers={"Authorization": f"Bearer {self.creds['access_token']}"})
        return HealthResult(r.status_code == 200, "Connected" if r.status_code == 200 else f"HTTP {r.status_code}: {r.text[:120]}")


class PipedriveAdapter(BaseAdapter):
    key = "pipedrive"
    env_map = {"api_token": "PIPEDRIVE_API_TOKEN", "company_domain": "PIPEDRIVE_COMPANY_DOMAIN"}
    required = ["api_token"]

    def _ping(self):
        r = self._get("https://api.pipedrive.com/v1/users/me", params={"api_token": self.creds["api_token"]})
        data = r.json()
        return HealthResult(bool(data.get("success")), "Connected" if data.get("success") else "Invalid token", data.get("data", {}))


class StripeAdapter(BaseAdapter):
    key = "stripe"
    env_map = {"secret_key": "STRIPE_SECRET_KEY", "webhook_secret": "STRIPE_WEBHOOK_SECRET"}
    required = ["secret_key"]

    def _ping(self):
        r = self._get("https://api.stripe.com/v1/balance", auth=(self.creds["secret_key"], ""))
        return HealthResult(r.status_code == 200, "Connected" if r.status_code == 200 else f"HTTP {r.status_code}", r.json() if r.status_code == 200 else {})


class SendGridAdapter(BaseAdapter):
    key = "sendgrid"
    env_map = {"api_key": "SENDGRID_API_KEY"}

    def _ping(self):
        r = self._get("https://api.sendgrid.com/v3/user/profile", headers={"Authorization": f"Bearer {self.creds['api_key']}"})
        return HealthResult(r.status_code == 200, "Connected" if r.status_code == 200 else f"HTTP {r.status_code}")


class ResendAdapter(BaseAdapter):
    key = "resend"
    env_map = {"api_key": "RESEND_API_KEY"}

    def _ping(self):
        r = self._get("https://api.resend.com/domains", headers={"Authorization": f"Bearer {self.creds['api_key']}"})
        return HealthResult(r.status_code == 200, "Connected" if r.status_code == 200 else f"HTTP {r.status_code}")


class SlackAdapter(BaseAdapter):
    key = "slack"
    env_map = {"bot_token": "SLACK_BOT_TOKEN", "channel": "SLACK_ALERTS_CHANNEL"}
    required = ["bot_token"]

    def _ping(self):
        r = self._get("https://slack.com/api/auth.test", headers={"Authorization": f"Bearer {self.creds['bot_token']}"})
        data = r.json()
        return HealthResult(bool(data.get("ok")), data.get("team", data.get("error", "")), data)


class SerpApiAdapter(BaseAdapter):
    key = "serpapi"
    env_map = {"api_key": "SERPAPI_API_KEY"}

    def _ping(self):
        r = self._get("https://serpapi.com/account", params={"api_key": self.creds["api_key"]})
        return HealthResult(r.status_code == 200, "Connected" if r.status_code == 200 else f"HTTP {r.status_code}", r.json() if r.status_code == 200 else {})


class FirecrawlAdapter(BaseAdapter):
    key = "firecrawl"
    env_map = {"api_key": "FIRECRAWL_API_KEY"}


class TavilyAdapter(BaseAdapter):
    key = "tavily"
    env_map = {"api_key": "TAVILY_API_KEY"}


class ElevenLabsAdapter(BaseAdapter):
    key = "elevenlabs"
    env_map = {"api_key": "ELEVENLABS_API_KEY"}

    def _ping(self):
        r = self._get("https://api.elevenlabs.io/v1/user", headers={"xi-api-key": self.creds["api_key"]})
        return HealthResult(r.status_code == 200, "Connected" if r.status_code == 200 else f"HTTP {r.status_code}")


class GenericEnvAdapter(BaseAdapter):
    """Fallback adapter built from the registry's env_vars list."""

    def __init__(self, provider: dict, credentials=None, config=None):
        self.key = provider["key"]
        fields = provider.get("fields") or []
        env_vars = provider.get("env_vars") or []
        self.env_map = {f: env_vars[i] for i, f in enumerate(fields) if i < len(env_vars)}
        self.required = list(self.env_map)
        super().__init__(credentials, config)


ADAPTERS = {a.key: a for a in [
    GroqAdapter, AnthropicAdapter, OpenAIAdapter,
    MetaAdsAdapter, GoogleAdsAdapter, LinkedInAdapter, TikTokAdsAdapter, ApolloAdapter, HunterAdapter,
    ZeroBounceAdapter, InstantlyAdapter, SmartleadAdapter, HubSpotAdapter, PipedriveAdapter, StripeAdapter, SendGridAdapter,
    ResendAdapter, SlackAdapter, SerpApiAdapter, FirecrawlAdapter, TavilyAdapter, ElevenLabsAdapter,
]}


def get_adapter(provider: dict, credentials=None, config=None) -> BaseAdapter:
    cls = ADAPTERS.get(provider["key"])
    if cls:
        return cls(credentials, config)
    return GenericEnvAdapter(provider, credentials, config)
