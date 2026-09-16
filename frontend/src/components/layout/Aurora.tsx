/** Ambient animated background used behind auth + hero surfaces. */
export function Aurora({ intensity = 1 }: { intensity?: number }) {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
      <div className="absolute -left-[10%] -top-[20%] h-[60vh] w-[60vw] rounded-full blur-3xl animate-aurora"
        style={{ background: `radial-gradient(closest-side, rgba(124,108,255,${0.35 * intensity}), transparent)` }} />
      <div className="absolute -right-[15%] top-[10%] h-[55vh] w-[55vw] rounded-full blur-3xl animate-aurora [animation-delay:-6s]"
        style={{ background: `radial-gradient(closest-side, rgba(34,211,238,${0.28 * intensity}), transparent)` }} />
      <div className="absolute bottom-[-30%] left-[25%] h-[60vh] w-[60vw] rounded-full blur-3xl animate-aurora [animation-delay:-12s]"
        style={{ background: `radial-gradient(closest-side, rgba(52,211,153,${0.18 * intensity}), transparent)` }} />
      <div className="absolute inset-0 bg-grid-fade [background-size:48px_48px] [mask-image:radial-gradient(ellipse_at_center,black_20%,transparent_75%)]" />
    </div>
  )
}
