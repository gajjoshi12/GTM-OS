import { useState } from 'react'
import { motion } from 'framer-motion'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Bot, ChevronRight, Play, RefreshCw, Zap } from 'lucide-react'
import { get, post, type Paginated } from '@/lib/api'
import { relTime } from '@/lib/format'
import { Badge, Button, Meter, Modal, PageHeader, Panel, statusTone } from '@/components/ui'

type Agent = { id: number; key: string; name: string; group: string; group_label: string; description: string; judged_on: string; status: string; enabled: boolean; runs_count: number; success_rate: number; health_score: number; last_run_at: string | null; last_summary: string; pending_decisions?: number }
type OrgChart = { cmo: Agent; groups: { key: string; label: string; agents: Agent[] }[] }
type Run = { id: number; agent_name: string; agent_key: string; trigger: string; status: string; mode: string; summary: string; log: { t: number; msg: string }[]; output: { findings?: string[]; decisions?: unknown[]; artifacts?: Record<string, unknown> }; duration_ms: number; created_at: string }

export function AgentsPage() {
  const qc = useQueryClient()
  const [selected, setSelected] = useState<Agent | null>(null)
  const { data: org } = useQuery({ queryKey: ['agents', 'org'], queryFn: () => get<OrgChart>('/agents/org-chart/'), refetchInterval: 15_000 })
  const { data: runs } = useQuery({ queryKey: ['runs', selected?.id], queryFn: () => get<Paginated<Run>>('/agents/runs/', { agent: selected?.id, page_size: 8 }), enabled: !!selected })
  const invalidate = () => { qc.invalidateQueries({ queryKey: ['agents'] }); qc.invalidateQueries({ queryKey: ['runs'] }); qc.invalidateQueries({ queryKey: ['decisions'] }); qc.invalidateQueries({ queryKey: ['activity'] }) }
  const runOne = useMutation({ mutationFn: (id: number) => post<Run>(`/agents/agents/${id}/run/`, {}), onSuccess: invalidate })
  const runAll = useMutation({ mutationFn: () => post('/agents/agents/run_all/', {}), onSuccess: invalidate })
  const total = org?.groups.flatMap((g) => g.agents).length ?? 0

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Agent orchestration" title={<>One AI CMO. <span className="gradient-text">{total} specialists.</span></>}
        description="The AI CMO owns the customer relationship end-to-end; every specialist reports upward. Run one agent, or trigger the full closed-loop pass."
        actions={<Button onClick={() => runAll.mutate()} loading={runAll.isPending}><Zap className="h-4 w-4" /> Run closed-loop pass</Button>} />

      {org?.cmo && (
        <motion.button initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} onClick={() => setSelected(org.cmo)}
          className="glass-strong relative w-full overflow-hidden p-6 text-left ring-1 ring-accent/30 transition hover:ring-accent/60">
          <div className="absolute -right-24 -top-24 h-64 w-64 rounded-full bg-accent/20 blur-3xl" />
          <div className="relative flex flex-wrap items-center gap-5">
            <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-accent to-accent-cyan shadow-glow">
              <Bot className="h-7 w-7 text-ink-950" />
              <span className="absolute -inset-2 rounded-3xl border border-accent/30 animate-pulseRing" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2"><h2 className="text-xl font-bold text-white">{org.cmo.name}</h2><Badge tone={statusTone(org.cmo.status)} dot>{org.cmo.status}</Badge></div>
              <p className="mt-1 max-w-3xl text-sm text-[var(--text-secondary)]">{org.cmo.description}</p>
              <p className="mt-2 text-xs text-[var(--text-muted)]">Judged on: {org.cmo.judged_on} · {org.cmo.runs_count} runs · last {relTime(org.cmo.last_run_at)}</p>
            </div>
            <div className="text-right"><div className="label">Health</div><div className="text-3xl font-bold text-white">{org.cmo.health_score}</div></div>
          </div>
        </motion.button>
      )}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {org?.groups.map((g, gi) => (
          <motion.div key={g.key} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: gi * 0.04 }}>
            <Panel title={g.label} subtitle={`${g.agents.length} agents`} padded={false} className="h-full">
              <div className="divide-y divide-white/[0.05] px-2 pb-2">
                {g.agents.map((a) => (
                  <button key={a.id} onClick={() => setSelected(a)} className="group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left transition hover:bg-white/[0.04]">
                    <span className="relative flex h-2 w-2 shrink-0">
                      {a.status === 'running' && <span className="absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-70 animate-pulseRing" />}
                      <span className={`relative inline-flex h-2 w-2 rounded-full ${a.status === 'running' ? 'bg-cyan-400' : a.status === 'error' ? 'bg-rose-400' : a.status === 'paused' ? 'bg-amber-400' : 'bg-emerald-400'}`} />
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2"><span className="truncate text-sm font-semibold text-white">{a.name}</span>{(a.pending_decisions ?? 0) > 0 && <span className="rounded-full bg-accent/20 px-1.5 font-mono text-[10px] text-accent-soft">{a.pending_decisions}</span>}</div>
                      <div className="truncate text-[11px] text-[var(--text-muted)]">{a.last_summary || a.judged_on}</div>
                    </div>
                    <div className="w-14"><Meter value={a.health_score} height={4} color={a.health_score > 90 ? 'var(--status-good)' : 'var(--status-warning)'} /></div>
                    <ChevronRight className="h-4 w-4 text-[var(--text-muted)] opacity-0 transition group-hover:opacity-100" />
                  </button>
                ))}
              </div>
            </Panel>
          </motion.div>
        ))}
      </div>

      <Modal open={!!selected} onClose={() => setSelected(null)} width="max-w-3xl" title={selected && (
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent/60 to-accent-cyan/60"><Bot className="h-5 w-5 text-white" /></div>
          <div><div className="text-base font-bold text-white">{selected.name}</div><div className="text-xs font-normal text-[var(--text-muted)]">{selected.group_label} · judged on {selected.judged_on}</div></div>
          <Badge tone={statusTone(selected.status)} dot className="ml-auto">{selected.status}</Badge>
        </div>
      )}>
        {selected && (
          <div className="space-y-4">
            <p className="text-sm text-[var(--text-secondary)]">{selected.description}</p>
            <div className="grid grid-cols-3 gap-3">
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3"><div className="label">Runs</div><div className="text-xl font-bold text-white">{selected.runs_count}</div></div>
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3"><div className="label">Success</div><div className="text-xl font-bold text-white">{Math.round(selected.success_rate * 100)}%</div></div>
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3"><div className="label">Last run</div><div className="text-xl font-bold text-white">{relTime(selected.last_run_at)}</div></div>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => runOne.mutate(selected.id)} loading={runOne.isPending}><Play className="h-4 w-4" /> Run now</Button>
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
                    {r.output?.findings?.length ? <div><div className="label mb-1">Findings</div><ul className="list-disc space-y-0.5 pl-4 text-[var(--text-secondary)]">{r.output.findings.map((f, i) => <li key={i}>{f}</li>)}</ul></div> : null}
                    <div><div className="label mb-1">Log</div><div className="rounded-lg bg-ink-950/70 p-2 font-mono text-[11px] text-[var(--text-secondary)]">{r.log.map((l, i) => <div key={i}><span className="text-accent-soft">[{l.t}]</span> {l.msg}</div>)}</div></div>
                  </div>
                </details>
              ))}
              {runs && runs.results.length === 0 && <div className="py-6 text-center text-xs text-[var(--text-muted)]">No runs yet — press Run now.</div>}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
