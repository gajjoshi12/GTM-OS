import { useEffect, type ReactElement } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { useAuth } from '@/store/auth'
import { AppShell } from '@/components/layout/AppShell'
import { LandingPage } from '@/pages/Landing'
import { LoginPage } from '@/pages/Login'
import { OnboardingPage } from '@/pages/Onboarding'
import { CommandCentre } from '@/pages/CommandCentre'
import { AgentsPage } from '@/pages/Agents'
import { IntelligencePage } from '@/pages/Intelligence'
import { ProspectsPage } from '@/pages/Prospects'
import { OutboundPage } from '@/pages/Outbound'
import { CampaignsPage } from '@/pages/Campaigns'
import { ContentPage } from '@/pages/Content'
import { ConversionPage } from '@/pages/Conversion'
import { ExperimentsPage } from '@/pages/Experiments'
import { AnalyticsPage } from '@/pages/Analytics'
import { IntegrationsPage } from '@/pages/Integrations'
import { SettingsPage } from '@/pages/Settings'

function Protected({ children }: { children: ReactElement }) {
  const { user, loading } = useAuth()
  const loc = useLocation()
  if (loading) return <Splash />
  if (!user) return <Navigate to="/landing" state={{ from: loc }} replace />
  if (!user.current_workspace?.onboarding_completed && loc.pathname !== '/onboarding') return <Navigate to="/onboarding" replace />
  return children
}

function Splash() {
  return (
    <div className="flex h-full items-center justify-center">
      <div className="relative">
        <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-accent to-accent-cyan shadow-glow animate-float" />
        <div className="absolute inset-0 m-auto h-4 w-4 rounded-full bg-ink-950" />
      </div>
    </div>
  )
}

export default function App() {
  const bootstrap = useAuth((s) => s.bootstrap)
  useEffect(() => { bootstrap() }, [bootstrap])

  return (
    <Routes>
      <Route path="/landing" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/onboarding" element={<Protected><OnboardingPage /></Protected>} />
      <Route element={<Protected><AppShell /></Protected>}>
        <Route path="/" element={<CommandCentre />} />
        <Route path="/agents" element={<AgentsPage />} />
        <Route path="/intelligence" element={<IntelligencePage />} />
        <Route path="/prospects" element={<ProspectsPage />} />
        <Route path="/outbound" element={<OutboundPage />} />
        <Route path="/campaigns" element={<CampaignsPage />} />
        <Route path="/content" element={<ContentPage />} />
        <Route path="/conversion" element={<ConversionPage />} />
        <Route path="/experiments" element={<ExperimentsPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/integrations" element={<IntegrationsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
