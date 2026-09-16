import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { channelColor, channelLabel, compact, dayLabel, money } from '@/lib/format'

/* Shared tooltip chrome ---------------------------------------------------- */
export function ChartTip({ active, payload, label, currency, fmt }: { active?: boolean; payload?: { name: string; value: number; color?: string; dataKey?: string }[]; label?: string; currency?: string; fmt?: (v: number, key: string) => string }) {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-strong min-w-[160px] px-3 py-2 text-xs">
      <div className="mb-1 font-semibold text-white">{label}</div>
      {payload.map((p) => (
        <div key={p.name} className="flex items-center justify-between gap-4 py-0.5">
          <span className="flex items-center gap-1.5 text-[var(--text-secondary)]"><span className="h-2 w-2 rounded-full" style={{ background: p.color }} />{p.name}</span>
          <span className="num font-semibold text-white">{fmt ? fmt(p.value, String(p.dataKey ?? p.name)) : currency ? money(p.value, currency) : compact(p.value)}</span>
        </div>
      ))}
    </div>
  )
}

/* Revenue vs Spend vs Pipeline -------------------------------------------- */
export function RevenueSpendChart({ data, currency, height = 260 }: { data: { date: string; revenue: number; spend: number; pipeline: number }[]; currency: string; height?: number }) {
  const rows = data.map((d) => ({ ...d, label: dayLabel(d.date) }))
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={rows} margin={{ top: 10, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="gRev" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="var(--series-1)" stopOpacity={0.28} /><stop offset="100%" stopColor="var(--series-1)" stopOpacity={0} /></linearGradient>
          <linearGradient id="gSpend" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="var(--series-2)" stopOpacity={0.22} /><stop offset="100%" stopColor="var(--series-2)" stopOpacity={0} /></linearGradient>
        </defs>
        <CartesianGrid vertical={false} strokeDasharray="0" />
        <XAxis dataKey="label" tickLine={false} axisLine={false} minTickGap={28} />
        <YAxis tickLine={false} axisLine={false} width={54} tickFormatter={(v) => money(v, currency, 0)} />
        <Tooltip content={<ChartTip currency={currency} />} cursor={{ stroke: 'var(--axis)' }} />
        <Area type="monotone" dataKey="revenue" name="Revenue" stroke="var(--series-1)" strokeWidth={2} fill="url(#gRev)" dot={false} activeDot={{ r: 4, strokeWidth: 2, stroke: 'var(--surface-1)' }} />
        <Area type="monotone" dataKey="spend" name="Spend" stroke="var(--series-2)" strokeWidth={2} fill="url(#gSpend)" dot={false} activeDot={{ r: 4, strokeWidth: 2, stroke: 'var(--surface-1)' }} />
      </AreaChart>
    </ResponsiveContainer>
  )
}

/* Channel CAC bars ---------------------------------------------------------- */
export function ChannelBars({ data, metric, currency, height = 220, label }: { data: { channel: string; [k: string]: number | string }[]; metric: string; currency?: string; height?: number; label: string }) {
  const rows = data.filter((d) => Number(d[metric]) > 0).map((d) => ({ ...d, name: channelLabel(d.channel) }))
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={rows} layout="vertical" margin={{ top: 4, right: 40, left: 8, bottom: 4 }} barCategoryGap={6}>
        <CartesianGrid horizontal={false} />
        <XAxis type="number" tickLine={false} axisLine={false} tickFormatter={(v) => currency ? money(v, currency, 0) : compact(v)} />
        <YAxis type="category" dataKey="name" tickLine={false} axisLine={false} width={96} />
        <Tooltip content={<ChartTip currency={currency} />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
        <Bar dataKey={metric} name={label} radius={[0, 4, 4, 0]} maxBarSize={22} label={{ position: 'right', fill: 'var(--text-secondary)', fontSize: 11, formatter: (v: unknown) => currency ? money(Number(v), currency, 0) : compact(Number(v)) }}>
          {rows.map((r) => <Cell key={r.channel} fill={channelColor(String(r.channel))} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

/* Funnel ------------------------------------------------------------------- */
export function Funnel({ data }: { data: { stage: string; count: number }[] }) {
  const max = Math.max(...data.map((d) => d.count), 1)
  return (
    <div className="space-y-2">
      {data.map((d, i) => (
        <div key={d.stage} className="flex items-center gap-3">
          <div className="w-24 text-right text-[11px] capitalize text-[var(--text-secondary)]">{d.stage}</div>
          <div className="relative h-5 flex-1 overflow-hidden rounded-md bg-white/[0.04]">
            <div className="h-full rounded-md transition-all" style={{ width: `${Math.max(2, (d.count / max) * 100)}%`, background: `color-mix(in oklab, var(--series-1) ${100 - i * 9}%, var(--surface-1))` }} />
          </div>
          <div className="num w-12 text-right text-xs font-semibold text-white">{d.count}</div>
        </div>
      ))}
    </div>
  )
}

/* Simple multi-line ------------------------------------------------------- */
export function MultiLine({ data, keys, height = 200, fmt }: { data: Record<string, number | string>[]; keys: { key: string; label: string; color: string }[]; height?: number; fmt?: (v: number) => string }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} />
        <XAxis dataKey="label" tickLine={false} axisLine={false} minTickGap={24} />
        <YAxis tickLine={false} axisLine={false} width={44} tickFormatter={(v) => fmt ? fmt(v) : compact(v)} />
        <Tooltip content={<ChartTip fmt={fmt ? (v) => fmt(v) : undefined} />} cursor={{ stroke: 'var(--axis)' }} />
        {keys.map((k) => <Line key={k.key} type="monotone" dataKey={k.key} name={k.label} stroke={k.color} strokeWidth={2} dot={false} activeDot={{ r: 4, strokeWidth: 2, stroke: 'var(--surface-1)' }} />)}
      </LineChart>
    </ResponsiveContainer>
  )
}

export function Legend({ items }: { items: { label: string; color: string }[] }) {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-[var(--text-secondary)]">
      {items.map((i) => <span key={i.label} className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full" style={{ background: i.color }} />{i.label}</span>)}
    </div>
  )
}
