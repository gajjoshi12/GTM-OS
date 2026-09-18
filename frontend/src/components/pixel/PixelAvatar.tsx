import { useEffect, useMemo, useRef, useState } from 'react'
import { clsx } from 'clsx'
import { frameUrl, lookFor, type FrameName } from './sprites'

export type AvatarState = 'idle' | 'working' | 'error' | 'paused'

/**
 * A little pixel person for one agent.
 *
 * The animation is driven by the agent's real status, so what you see on screen
 * is what the backend is actually doing:
 *   working -> types at the keyboard, bobs faster, throws off sparkles
 *   idle    -> breathes slowly and blinks every few seconds
 *   error   -> closes its eyes and sweats
 */
export function PixelAvatar({ seed, state = 'idle', size = 64, className, desk = false }: {
  seed: string
  state?: AvatarState
  size?: number
  className?: string
  /** Draw a small desk shadow under the character. */
  desk?: boolean
}) {
  const working = state === 'working'
  const [frame, setFrame] = useState<FrameName>('idle')

  // Stable per-agent phase so 38 avatars don't blink in unison.
  const phase = useMemo(() => {
    let h = 0
    for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0
    return (h % 1000) / 1000
  }, [seed])

  const timers = useRef<number[]>([])
  useEffect(() => {
    timers.current.forEach(clearTimeout)
    timers.current = []
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

    if (state === 'error') { setFrame('error'); return }
    if (reduce) { setFrame(working ? 'work1' : 'idle'); return }

    if (working) {
      // Typing: alternate hand positions ~5fps.
      setFrame('work1')
      const id = window.setInterval(() => setFrame((f) => (f === 'work1' ? 'work2' : 'work1')), 190)
      timers.current.push(id)
      return () => clearInterval(id)
    }

    // Idle: blink for ~140ms every 3–7s.
    setFrame('idle')
    let alive = true
    const loop = (first = false) => {
      const wait = (first ? 600 + phase * 3000 : 3000 + Math.random() * 4000)
      const t = window.setTimeout(() => {
        if (!alive) return
        setFrame('blink')
        const t2 = window.setTimeout(() => { if (alive) { setFrame('idle'); loop() } }, 140)
        timers.current.push(t2)
      }, wait)
      timers.current.push(t)
    }
    loop(true)
    return () => { alive = false; timers.current.forEach(clearTimeout) }
  }, [state, working, phase])

  const src = frameUrl(seed, frame)
  const accent = lookFor(seed).palette.C

  return (
    <div className={clsx('relative shrink-0 select-none', className)} style={{ width: size, height: size }}>
      {desk && (
        <span className="absolute bottom-0 left-1/2 -translate-x-1/2 rounded-[50%] bg-black/40 blur-[3px]"
          style={{ width: size * 0.62, height: size * 0.1 }} aria-hidden />
      )}

      <img src={src} alt="" aria-hidden draggable={false}
        className={clsx('h-full w-full', working ? 'animate-[pixWork_.42s_ease-in-out_infinite]' : 'animate-[pixBob_3.4s_ease-in-out_infinite]')}
        style={{ imageRendering: 'pixelated', animationDelay: `${-phase * 3}s` }} />

      {/* sparkles only while it is genuinely working */}
      {working && (
        <>
          {[0, 1, 2].map((i) => (
            <span key={i} aria-hidden
              className="absolute rounded-[1px] animate-[pixSpark_1.5s_ease-out_infinite]"
              style={{
                left: `${18 + i * 26}%`, top: '34%',
                width: Math.max(2, size * 0.045), height: Math.max(2, size * 0.045),
                background: i === 1 ? '#22d3ee' : accent,
                animationDelay: `${i * 0.45 + phase * 0.5}s`,
                ['--dx' as string]: `${(i - 1) * 8}px`,
              }} />
          ))}
        </>
      )}
    </div>
  )
}

/** Small round badge version — for decision cards, activity rows, command results. */
export function PixelChip({ seed, state = 'idle', size = 32, ring = true, className }: {
  seed: string; state?: AvatarState; size?: number; ring?: boolean; className?: string
}) {
  return (
    <span className={clsx('relative inline-flex shrink-0 items-end justify-center overflow-hidden rounded-xl',
      ring && 'ring-1 ring-white/10', className)}
      style={{ width: size, height: size, background: 'linear-gradient(160deg, rgba(255,255,255,0.09), rgba(255,255,255,0.02))' }}>
      {/* scale up a touch and crop to the head+shoulders */}
      <PixelAvatar seed={seed} state={state} size={size * 1.28} className="!absolute -bottom-[14%]" />
    </span>
  )
}
