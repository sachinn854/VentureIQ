import { motion, AnimatePresence } from 'framer-motion'
import { stripMarkdown } from '../utils/stripMarkdown'

const AGENTS = [
  { key: 'market_research',       label: 'Market Research',  icon: '📊', accent: '#3B82F6', light: '#EFF6FF', border: '#BFDBFE' },
  { key: 'competitor_analysis',   label: 'Competitors',      icon: '🔍', accent: '#8B5CF6', light: '#F5F3FF', border: '#DDD6FE' },
  { key: 'financial_feasibility', label: 'Financials',       icon: '💰', accent: '#F59E0B', light: '#FFFBEB', border: '#FDE68A' },
  { key: 'risk_assessment',       label: 'Risk Assessment',  icon: '⚠️', accent: '#EF4444', light: '#FFF1F2', border: '#FECDD3' },
]

function StatusPill({ status, accent }) {
  if (!status || status === 'idle')
    return <span className="text-[10px] font-semibold text-slate-400 bg-slate-100 px-2.5 py-1 rounded-full">Idle</span>
  if (status === 'running')
    return <span className="text-[10px] font-semibold text-blue-600 bg-blue-50 border border-blue-200 px-2.5 py-1 rounded-full animate-pulse">Running...</span>
  if (status === 'complete')
    return <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full">Done ✓</span>
  if (status === 'error')
    return <span className="text-[10px] font-semibold text-rose-600 bg-rose-50 border border-rose-200 px-2.5 py-1 rounded-full">Error</span>
  return null
}

function ScoreRing({ score, color }) {
  if (score == null) return null
  const size = 48, stroke = 4, r = (size - stroke) / 2
  const circ = 2 * Math.PI * r
  const fill = (score / 10) * 0.75
  const offset = circ * (1 - fill)
  const ringColor = score >= 7 ? '#10B981' : score >= 5 ? '#F59E0B' : '#EF4444'

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(135deg)' }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#E5E7EB" strokeWidth={stroke} strokeDasharray={circ * 0.75} strokeLinecap="round" />
        <motion.circle
          cx={size/2} cy={size/2} r={r} fill="none" stroke={ringColor} strokeWidth={stroke}
          strokeDasharray={circ * 0.75}
          initial={{ strokeDashoffset: circ * 0.75 }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute text-center">
        <p className="text-[11px] font-bold text-slate-700 leading-none">{score?.toFixed(1)}</p>
      </div>
    </div>
  )
}

function MetaChip({ label, value }) {
  return (
    <div className="flex items-center gap-1.5 bg-white border border-slate-100 rounded-lg px-2.5 py-1.5">
      <span className="text-[10px] text-slate-400 font-medium">{label}</span>
      <span className="text-[10px] text-slate-700 font-bold">{value}</span>
    </div>
  )
}

function AgentCard({ agent, status, data }) {
  const isIdle     = !status || status === 'idle'
  const isRunning  = status === 'running'
  const isComplete = status === 'complete'
  const isError    = status === 'error'
  const score = data?.market_score ?? data?.competition_score ?? data?.financial_score ?? data?.risk_score

  return (
    <motion.div
      layout
      className="flex flex-col rounded-2xl border bg-white shadow-sm overflow-hidden transition-all duration-300"
      style={{ borderColor: isComplete ? agent.border : isRunning ? agent.border : '#E2E8F0' }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3 border-b"
        style={{
          background: isComplete || isRunning ? agent.light : '#F8FAFC',
          borderColor: isComplete ? agent.border : isRunning ? agent.border : '#F1F5F9',
        }}
      >
        <div className="flex items-center gap-2">
          <span className="text-base">{agent.icon}</span>
          <span className="text-xs font-bold text-slate-700">{agent.label}</span>
        </div>
        <StatusPill status={status} />
      </div>

      {/* Body */}
      <div className="flex-1 p-4 min-h-[140px]">
        {isIdle && (
          <div className="h-full flex flex-col justify-center items-center gap-2 opacity-40">
            <div className="w-8 h-8 rounded-full border-2 border-dashed border-slate-300 flex items-center justify-center">
              <span className="text-slate-400 text-xs">○</span>
            </div>
            <p className="text-xs text-slate-400">Waiting...</p>
          </div>
        )}

        {isRunning && (
          <div className="space-y-2.5">
            {[90, 70, 80].map((w, i) => (
              <div key={i} className="h-2.5 rounded-full bg-slate-100 animate-pulse" style={{ width: `${w}%`, animationDelay: `${i * 0.2}s` }} />
            ))}
            <div className="h-2.5 rounded-full bg-slate-100 animate-pulse w-1/2" style={{ animationDelay: '0.6s' }} />
          </div>
        )}

        {isError && (
          <div className="h-full flex flex-col justify-center items-center gap-2 text-center">
            <span className="text-2xl opacity-60">⚠️</span>
            <p className="text-xs text-rose-500 font-medium">Agent error — partial data used</p>
          </div>
        )}

        {isComplete && data && (
          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
              className="space-y-3"
            >
              <div className="flex items-start gap-3">
                <ScoreRing score={score} />
                <p className="text-xs text-slate-600 leading-relaxed flex-1">{stripMarkdown(data.summary)}</p>
              </div>

              <div className="flex flex-wrap gap-2">
                {data.tam         && <MetaChip label="TAM"       value={data.tam} />}
                {data.growth_rate && <MetaChip label="Growth"    value={data.growth_rate} />}
                {data.market_gap  && <MetaChip label="Gap"       value={data.market_gap?.slice(0, 40) + (data.market_gap?.length > 40 ? '…' : '')} />}
                {data.ltv_cac_ratio !== undefined && <MetaChip label="LTV:CAC" value={`${data.ltv_cac_ratio}x`} />}
                {data.breakeven_months !== undefined && <MetaChip label="Breakeven" value={`${data.breakeven_months}mo`} />}
              </div>
            </motion.div>
          </AnimatePresence>
        )}
      </div>
    </motion.div>
  )
}

export default function StreamingPanel({ agentStatuses, agentData }) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {AGENTS.map(agent => (
        <AgentCard
          key={agent.key}
          agent={agent}
          status={agentStatuses[agent.key]}
          data={agentData[agent.key]}
        />
      ))}
    </div>
  )
}
