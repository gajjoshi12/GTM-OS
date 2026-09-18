import { useCallback, useState } from 'react'
import { motion } from 'framer-motion'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ChevronRight, Play, RefreshCw, Zap } from 'lucide-react'
import { get, post, type Paginated } from '@/lib/api'
import { relTime } from '@/lib/format'
import { Badge, Button, Meter, Modal, PageHeader, Panel, Tabs, statusTone } from '@/components/ui'
import { AgentOrbit } from '@/components/AgentOrbit'
import { TeamRoom, avatarState, type TeamAgent } from '@/components/pixel/TeamRoom'
import { PixelAvatar } from '@/components/pixel/PixelAvatar'

type Agent = TeamAgent & {
  description: string; judged_on: string; enabled: boolean; runs_count: number; success_rate: number
}
type OrgChart = { cmo: Agent; groups: { key: string; label: string; agents: Agent[] }[] }
type Run = {
  id: number; agent_name: string; agent_key: string; trigger: string; status: string; mode: string; summary: string
  log: { t: number; msg: string }[]; output: { findings?: string[]; decisions?: unknown[]; artifacts?: Record<string, unknown> }
  duration_ms: number; created_at: string
}

export function AgentsPage() {
  const qc = useQueryClient()
  const [selected, setSelected] = useState<Agent | null>(null)
  const [view, setView] = useState<'team' | 'orbit' | 'list'>('team')

  // Agents the UI knows are working *right now* because we are mid-request.
  // Runs are synchronous, so without this the typing animation would never show
  // for an agent you just triggered yourself.
  const [busy, setBusy] = useState<Set<number>>(new Set())
  const markBusy = useCallback((ids: number[], on: boolean) => {
    setBusy((prev) => {
      const next = new Set(prev)
      ids.forEach((id) => (on ? next.add(id) : next.delete(id)))
      return next
    })
  }, [])

  const { data: org } = useQuery({ queryKey: ['agents', 'org'], queryFn: () => get<OrgChart>('/agents/org-chart/'), refetchInterval: 15_000 })
  const { data: runs } = useQuery({ queryKey: ['runs', selected?.id], queryFn: () => get<Paginated<Run>>('/agents/runs/', { agent: selected?.id, page_size: 8 }), enabled: !!selected })

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['agents'] }); qc.invalidateQueries({ queryKey: ['runs'] })
    qc.invalidateQueries({ queryKey: ['decisions'] }); qc.invalidateQueries({ queryKey: ['activity'] })
    qc.invalidateQueries({ queryKey: ['dashboard'] })
  }
  const runOne = useMutation({
    mutationFn: (id: number) => post<Run>(`/agents/agents/${id}/run/`, {}),
    onMutate: (id) => markBusy([id], true),
    onSettled: (_d, _e, id) => { markBusy([id], false); invalidate() },
  })
  const everyId = [org?.cmo?.id, ...(org?.groups.flatMap((g) => g.agents.map((a) => a.id)) ?? [])].filter(Boolean) as number[]
  const runAll = useMutation({
    mutationFn: () => post('/agents/agents/run_all/', {}),
    onMutate: () => markBusy(everyId, true),
    onSettled: () => { markBusy(everyId, false); invalidate() },
  })

  const total = org?.groups.flatMap((g) => g.agents).length ?? 0
  const groupsWithLabel = org?.groups.map((g) => ({ ...g, agents: g.agents.map((a) => ({ ...a, group_label: g.label })) })) ?? []

  return (
    <div className="space-y-6">
      <PageHeader title={<>Your AI <span className="gradient-text">marketing team</span></>}
        description={`One manager and ${total} specialists. Each has a single job. Hover anyone to see what they last did, or click to read their full working history.`}
        actions={<>
          <Tabs tabs={[{ key: 'team', label: 'Team' }, { key: 'orbit', label: 'Orbit' }, { key: 'list', label: 'List' }]} value={view} onChange={setView} />
          <Button onClick={() => runAll.mutate()} loading={runAll.isPending}><Zap className="h-4 w-4" /> Put everyone to work</Button>
        </>} />

      {view === 'team' && org && (
        <TeamRoom cmo={org.cmo} groups={groupsWithLabel} busy={busy} onSelect={(a) => setSelected(a as Agent)} />
      )}

      {view === 'orbit' && org && (
        <Panel title="The whole team, live" subtitle="The manager in the middle, every specialist orbiting by department. Glowing dots are working right now — hover one.">
          <AgentOrbit cmo={org.cmo} agents={groupsWithLabel.flatMap((g) => g.agents)} onSelect={(a) => setSelected(a as Agent)} />
        </Panel>
      )}

      {view === 'list' && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {groupsWithLabel.map((g, gi) => (
            <motion.div key={g.key} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: gi * 0.04 }}>
              <Panel title={g.label} subtitle={`${g.agents.length} agents`} padded={false} className="h-full">
                <div className="divide-y divide-white/[0.05] px-2 pb-2">
                  {g.agents.map((a) => (
                    <button key={a.id} onClick={() => setSelected(a)} className="group flex w-full items-center gap-3 rounded-xl px-2 py-2 text-left transition hover:bg-white/[0.04]">
                      <PixelAvatar seed={a.key} state={avatarState(a.status, busy.has(a.id))} size={34} />
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="truncate text-sm font-semibold text-white">{a.name}</span>
                          {(a.pending_decisions ?? 0) > 0 && <span className="rounded-full bg-accent/20 px-1.5 font-mono text-[10px] text-accent-soft">{a.pending_decisions}</span>}
                        </div>
                        <div className="truncate text-[11px] text-[var(--text-muted)]">{a.last_summary || a.judged_on}</div>
                      </div>
                      <div className="w-12"><Meter value={a.health_score} height={4} color={a.health_score > 90 ? 'var(--status-good)' : 'var(--status-warning)'} /></div>
                      <ChevronRight className="h-4 w-4 text-[var(--text-muted)] opacity-0 transition group-hover:opacity-100" />
                    </button>
                  ))}
                </div>
              </Panel>
            </motion.div>
          ))}
        </div>
      )}

      <Modal open={!!selected} onClose={() => setSelected(null)} width="max-w-3xl" title={selected && (
        <div className="flex items-center gap-3">
          <PixelAvatar seed={selected.key} state={avatarState(selected.status, busy.has(selected.id))} size={52} />
          <div>
            <div className="text-base font-bold text-white">{selected.name}</div>
            <div className="text-xs font-normal text-[var(--text-muted)]">{selected.group_label} · measured on {selected.judged_on}</div>
          </div>
          <Badge tone={statusTone(selected.status)} dot className="ml-auto">{selected.status === 'running' ? 'working' : selected.status}</Badge>
        </div>
      )}>
        {selected && (
          <div className="space-y-4">
            <p className="text-sm text-[var(--text-secondary)]">{selected.description}</p>
            <div className="grid grid-cols-3 gap-3">
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3"><div className="label">Times run</div><div className="text-xl font-bold text-white">{selected.runs_count}</div></div>
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3"><div className="label">Worked</div><div className="text-xl font-bold text-white">{Math.round(selected.success_rate * 100)}%</div></div>
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3"><div className="label">Last run</div><div className="text-xl font-bold text-white">{relTime(selected.last_run_at)}</div></div>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => runOne.mutate(selected.id)} loading={runOne.isPending}><Play className="h-4 w-4" /> Run this agent</Button>
              <Button variant="outline" onClick={() => qc.invalidateQueries({ queryKey: ['runs'] })}><RefreshCw className="h-4 w-4" /> Refresh</Button>
            </div>
            <div className="max-h-[42vh] space-y-2 overflow-y-auto pr-1">
              {runs?.results.map((r) => (
                <details key={r.id} className="group rounded-xl border border-white/[0.06] bg-white/[0.02] open:bg-white/[0.04]">
                  <summary className="flex cursor-pointer items-center gap-3 px-3 py-2.5 text-sm">
                    <Badge tone={statusTone(r.status)}>{r.status}</Badge>
                    <span className="min-w-0 flex-1 truncate text-white">{r.summary}</span>
                    <span className="font-mono text-[10px] text-[var(--text-muted)]">{r.mode} · {(r.duration_ms / 1000).toFixed(1)}s · {relTime(r.created_at)}</span>
                  </summary>
                  <div className="space-y-3 border-t border-white/[0.05] px-3 py-3 text-xs">
                    {r.output?.findings?.length ? <div><div className="label mb-1">What it found</div><ul className="list-disc space-y-0.5 pl-4 text-[var(--text-secondary)]">{r.output.findings.map((f, i) => <li key={i}>{f}</li>)}</ul></div> : null}
                    <div><div className="label mb-1">Step by step</div><div className="rounded-lg bg-ink-950/70 p-2 font-mono text-[11px] text-[var(--text-secondary)]">{r.log.map((l, i) => <div key={i}><span className="text-accent-soft">[{l.t}]</span> {l.msg}</div>)}</div></div>
                  </div>
                </details>
              ))}
              {runs && runs.results.length === 0 && <div className="py-6 text-center text-xs text-[var(--text-muted)]">Has not run yet — press the button above.</div>}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
