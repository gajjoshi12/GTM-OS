import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowRight, Bot, CheckCircle2, Command as CommandIcon, Loader2, Sparkles, X } from 'lucide-react'
import { get, post } from '@/lib/api'
import { Badge } from '@/components/ui'
import { PixelChip } from '@/components/pixel/PixelAvatar'

type Run = { id: number; agent_key: string; agent_name: string; status: string; summary: string; duration_ms: number }
type Command = { id: number; text: string; intent: string; response: string; runs: Run[]; plan: { assumptions?: string[]; expected_outcome?: string } }

export function useCommandBar() {
  const [open, setOpen] = useState(false)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); setOpen((o) => !o) }
      if (e.key === 'Escape') setOpen(false)
    }
    const onOpen = () => setOpen(true)
    window.addEventListener('keydown', onKey)
    window.addEventListener('gtm:command', onOpen)
    return () => { window.removeEventListener('keydown', onKey); window.removeEventListener('gtm:command', onOpen) }
  }, [])
  return { open, setOpen }
}

export function openCommandBar() { window.dispatchEvent(new CustomEvent('gtm:command')) }

export function CommandBar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [text, setText] = useState('')
  const [result, setResult] = useState<Command | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const qc = useQueryClient()
  const { data: suggestions = [] } = useQuery({ queryKey: ['command-suggestions'], queryFn: () => get<string[]>('/agents/commands/suggestions/'), staleTime: Infinity })

  const run = useMutation({
    mutationFn: (t: string) => post<Command>('/agents/commands/', { text: t }),
    onSuccess: (data) => {
      setResult(data)
      qc.invalidateQueries({ queryKey: ['decisions'] })
      qc.invalidateQueries({ queryKey: ['activity'] })
      qc.invalidateQueries({ queryKey: ['agents'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })

  useEffect(() => { if (open) setTimeout(() => inputRef.current?.focus(), 30); else { setResult(null); setText('') } }, [open])

  const submit = (t = text) => { if (t.trim()) { setText(t); run.mutate(t.trim()) } }

  return (
    <AnimatePresence>
      {open && (
        <motion.div className="fixed inset-0 z-[60] flex items-start justify-center px-4 pt-[10vh]" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <div className="absolute inset-0 bg-ink-950/70 backdrop-blur-md" onClick={onClose} />
          <motion.div initial={{ opacity: 0, y: -12, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -8, scale: 0.98 }} transition={{ type: 'spring', stiffness: 380, damping: 32 }}
            className="glass-strong relative w-full max-w-2xl overflow-hidden">
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-accent to-transparent" />
            <div className="flex items-center gap-3 border-b border-line px-5 py-4">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-accent-cyan">
                <Sparkles className="h-4 w-4 text-ink-950" />
              </div>
              <input ref={inputRef} value={text} onChange={(e) => setText(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && submit()}
                placeholder="Tell the AI CMO what you want… e.g. “Get me 50 enterprise meetings next month”"
                className="flex-1 bg-transparent text-[15px] text-white placeholder:text-[var(--text-muted)] outline-none" />
              {run.isPending ? <Loader2 className="h-4 w-4 animate-spin text-accent-soft" /> : (
                <button onClick={() => submit()} className="rounded-lg bg-white/[0.06] p-1.5 text-white hover:bg-white/10"><ArrowRight className="h-4 w-4" /></button>
              )}
              <button onClick={onClose} className="rounded-lg p-1.5 text-[var(--text-muted)] hover:text-white"><X className="h-4 w-4" /></button>
            </div>

            <div className="max-h-[60vh] overflow-y-auto p-5">
              {!result && !run.isPending && (
                <>
                  <div className="label mb-2">Try asking</div>
                  <div className="grid gap-1.5">
                    {suggestions.map((s) => (
                      <button key={s} onClick={() => submit(s)} className="group flex items-center gap-3 rounded-xl px-3 py-2 text-left text-sm text-[var(--text-secondary)] transition hover:bg-white/[0.05] hover:text-white">
                        <CommandIcon className="h-3.5 w-3.5 text-[var(--text-muted)] group-hover:text-accent-soft" />{s}
                      </button>
                    ))}
                  </div>
                </>
              )}

              {run.isPending && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm text-white"><Bot className="h-4 w-4 text-accent-soft" /> AI CMO is interpreting and delegating…</div>
                  {[0, 1, 2].map((i) => <div key={i} className="shimmer h-10 rounded-xl" />)}
                </div>
              )}

              {result && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge tone="accent">intent · {result.intent.replace(/_/g, ' ')}</Badge>
                    <Badge tone="good" dot>{result.runs.filter((r) => r.status === 'succeeded').length}/{result.runs.length} agents completed</Badge>
                  </div>
                  <p className="text-sm leading-relaxed text-white">{result.response}</p>
                  {result.plan?.expected_outcome && <p className="text-xs text-[var(--text-secondary)]"><span className="text-[var(--text-muted)]">Expected outcome:</span> {result.plan.expected_outcome}</p>}
                  <div className="space-y-1.5">
                    {result.runs.map((r, i) => (
                      <motion.div key={r.id} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                        className="flex items-start gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] px-3 py-2">
                        <PixelChip seed={r.agent_key} size={30} />
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-xs font-semibold text-white">{r.agent_name}</span>
                            <span className="font-mono text-[10px] text-[var(--text-muted)]">{(r.duration_ms / 1000).toFixed(1)}s</span>
                          </div>
                          <p className="mt-0.5 text-xs leading-relaxed text-[var(--text-secondary)]">{r.summary}</p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                  <div className="flex justify-end gap-2">
                    <button onClick={() => { setResult(null); setText('') }} className="text-xs text-[var(--text-muted)] hover:text-white">New command</button>
                  </div>
                </motion.div>
              )}
            </div>
            <div className="flex items-center gap-3 border-t border-line px-5 py-2.5 text-[11px] text-[var(--text-muted)]">
              <span><span className="kbd">↵</span> run</span><span><span className="kbd">esc</span> close</span><span className="ml-auto">Decisions appear in the feed for approval</span>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
