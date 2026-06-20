import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { stripMarkdown } from '../utils/stripMarkdown'

const SCORE_DIMS = [
  { key: 'market',      label: 'Market',      color: '#3B82F6' },
  { key: 'competition', label: 'Competition', color: '#8B5CF6' },
  { key: 'financial',   label: 'Financial',   color: '#F59E0B' },
  { key: 'risk',        label: 'Risk',        color: '#EF4444' },
]

const PIVOT_COLORS = { High: 'text-green-700 bg-green-50 border-green-200', Medium: 'text-yellow-700 bg-yellow-50 border-yellow-200', Low: 'text-gray-600 bg-gray-50 border-gray-200' }

function ScoreGauge({ score }) {
  const size   = 140
  const stroke = 10
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const arcFraction   = (score / 10) * 0.75
  const dashoffset    = circumference * (1 - arcFraction)
  const color = score >= 6 ? '#10B981' : score >= 4 ? '#F59E0B' : '#EF4444'

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(135deg)' }}>
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="#E5E7EB" strokeWidth={stroke} strokeDasharray={circumference * 0.75} strokeDashoffset={0} strokeLinecap="round" />
        <motion.circle
          cx={size/2} cy={size/2} r={radius} fill="none" stroke={color} strokeWidth={stroke}
          strokeDasharray={circumference * 0.75}
          initial={{ strokeDashoffset: circumference * 0.75 }}
          animate={{ strokeDashoffset: dashoffset }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute text-center">
        <motion.p className="text-3xl font-bold text-gray-800" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
          {score.toFixed(1)}
        </motion.p>
        <p className="text-xs text-gray-400 font-medium">/ 10</p>
      </div>
    </div>
  )
}

function ScoreBar({ label, score, color }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-600 font-medium">{label}</span>
        <span className="text-gray-800 font-semibold">{score?.toFixed(1)}</span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          animate={{ width: `${(score / 10) * 100}%` }}
          transition={{ duration: 0.8, ease: 'easeOut', delay: 0.3 }}
        />
      </div>
    </div>
  )
}

function ListSection({ title, items, icon, color }) {
  return (
    <div>
      <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-1.5">
        <span>{icon}</span> {title}
      </h4>
      <ul className="space-y-1.5">
        {items?.map((item, i) => (
          <motion.li
            key={i}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 * i }}
            className="flex items-start gap-2 text-sm text-gray-600"
          >
            <span className={`mt-0.5 w-1.5 h-1.5 rounded-full shrink-0 ${color}`} />
            {stripMarkdown(item)}
          </motion.li>
        ))}
      </ul>
    </div>
  )
}

function RevenueChart({ projections }) {
  if (!projections || projections.length === 0) return null
  const BAR_COLORS = ['#3B82F6', '#6366F1', '#8B5CF6']

  return (
    <div>
      <h4 className="text-sm font-semibold text-gray-700 mb-3">Revenue Projection</h4>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={projections} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#6B7280' }} axisLine={false} tickLine={false} />
          <YAxis hide />
          <Tooltip
            formatter={(value, name) => {
              const item = projections.find(p => p.revenue_inr === value)
              return [item?.label || value, 'Revenue']
            }}
            contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }}
          />
          <Bar dataKey="revenue_inr" radius={[6, 6, 0, 0]}>
            {projections.map((_, i) => (
              <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex justify-around mt-1">
        {projections.map((p, i) => (
          <div key={i} className="text-center">
            <p className="text-xs font-semibold text-gray-700">{p.label}</p>
            <p className="text-xs text-gray-400">{p.year}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function PivotSection({ pivots }) {
  if (!pivots?.pivots?.length) return null
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="border border-amber-200 bg-amber-50 rounded-xl p-4 space-y-3"
    >
      <div>
        <h4 className="text-sm font-bold text-amber-800 flex items-center gap-2">
          <span>🔄</span> Pivot Advisor
        </h4>
        <p className="text-xs text-amber-700 mt-0.5">{pivots.reasoning}</p>
      </div>
      <div className="space-y-2">
        {pivots.pivots.map((p, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.15 * i }}
            className="bg-white rounded-lg border border-amber-100 p-3"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-semibold text-gray-800">{p.title}</span>
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${PIVOT_COLORS[p.potential] || PIVOT_COLORS.Low}`}>
                {p.potential}
              </span>
            </div>
            <p className="text-xs text-gray-600 mb-1">{p.description}</p>
            <p className="text-xs text-amber-700 font-medium">Key change: {p.key_change}</p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

export default function VerdictCard({ report, pivots, financialData, onDownload }) {
  if (!report) return null
  const isGo = report.verdict === 'GO'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full rounded-2xl border border-gray-200 bg-white shadow-md overflow-hidden"
    >
      {/* Header */}
      <div className={`px-6 py-4 flex items-center justify-between ${isGo ? 'bg-green-50 border-b border-green-100' : 'bg-rose-50 border-b border-rose-100'}`}>
        <div className="flex items-center gap-3">
          <span className="text-3xl">{isGo ? '✅' : '❌'}</span>
          <div>
            <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Verdict</p>
            <p className={`text-2xl font-bold ${isGo ? 'text-green-700' : 'text-rose-700'}`}>{report.verdict}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-400">Confidence</p>
          <p className="text-xl font-bold text-gray-700">{report.confidence}%</p>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Score + Breakdown */}
        <div className="flex flex-col sm:flex-row items-center gap-6">
          <ScoreGauge score={report.overall_score} />
          <div className="flex-1 space-y-3 w-full">
            {SCORE_DIMS.map(d => (
              <ScoreBar key={d.key} label={d.label} score={report.score_breakdown?.[d.key]} color={d.color} />
            ))}
          </div>
        </div>

        {/* Revenue Chart */}
        {financialData?.revenue_projections?.length > 0 && (
          <div className="bg-gray-50 rounded-xl p-4">
            <RevenueChart projections={financialData.revenue_projections} />
          </div>
        )}

        {/* Executive Summary */}
        <div className="bg-gray-50 rounded-xl p-4">
          <p className="text-xs text-gray-400 font-semibold uppercase tracking-wide mb-1.5">Executive Summary</p>
          <p className="text-sm text-gray-700 leading-relaxed">{stripMarkdown(report.executive_summary)}</p>
        </div>

        {/* Strengths / Risks / Next Steps */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <ListSection title="Top Strengths" items={report.top_3_strengths}        icon="💪" color="bg-green-500" />
          <ListSection title="Key Risks"     items={report.top_3_risks}            icon="⚠️" color="bg-rose-500"  />
          <ListSection title="Next Steps"    items={report.recommended_next_steps} icon="🚀" color="bg-blue-500"  />
        </div>

        {/* Pivot Section — only for NO-GO */}
        {!isGo && <PivotSection pivots={pivots} />}

        {/* Download */}
        <div className="flex justify-end">
          <button
            onClick={onDownload}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-5 py-2.5 rounded-xl shadow transition"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download PDF Report
          </button>
        </div>
      </div>
    </motion.div>
  )
}
