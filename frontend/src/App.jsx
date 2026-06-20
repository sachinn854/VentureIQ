import { useState, useCallback, useRef } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import IdeaInput      from './components/IdeaInput'
import AgentGraph     from './components/AgentGraph'
import StreamingPanel from './components/StreamingPanel'
import VerdictCard    from './components/VerdictCard'
import ChatPanel      from './components/ChatPanel'
import ChatWidget     from './components/ChatWidget'
import { useWebSocket } from './hooks/useWebSocket'

const INITIAL_STATUSES = {}
const INITIAL_DATA     = {}

const STATS = [
  { label: '7 AI Agents',         icon: '🤖' },
  { label: 'Real-time Web Search', icon: '🌐' },
  { label: 'GO / NO-GO Verdict',  icon: '⚡' },
  { label: 'PDF Report',          icon: '📄' },
]

export default function App() {
  const [phase, setPhase]                   = useState('idle')
  const [agentStatuses, setAgentStatuses]   = useState(INITIAL_STATUSES)
  const [agentData, setAgentData]           = useState(INITIAL_DATA)
  const [finalReport, setFinalReport]       = useState(null)
  const [pivotSuggestions, setPivotSuggestions] = useState(null)
  const [error, setError]                   = useState(null)
  const [resetKey, setResetKey]             = useState(0)
  const runIdRef = useRef(null)

  const handleEvent = useCallback((event) => {
    switch (event.type) {
      case 'agent_start':
        setAgentStatuses(prev => ({ ...prev, [event.agent]: 'running' }))
        break
      case 'agent_complete':
        setAgentStatuses(prev => ({ ...prev, [event.agent]: 'complete' }))
        setAgentData(prev => ({ ...prev, [event.agent]: event.data }))
        break
      case 'final_report':
        setFinalReport(event.data)
        break
      case 'pivot_suggestions':
        setPivotSuggestions(event.data)
        break
      case 'error':
        if (event.agent !== 'synthesizer') {
          setAgentStatuses(prev => ({ ...prev, [event.agent]: 'error' }))
        } else {
          setError(event.message || 'Analysis failed.')
        }
        break
      case 'done':
        setPhase('done')
        break
      default:
        break
    }
  }, [])

  const { connect, disconnect } = useWebSocket({ onEvent: handleEvent })

  const handleSubmit = async (idea) => {
    disconnect()
    setPhase('running')
    setAgentStatuses(INITIAL_STATUSES)
    setAgentData(INITIAL_DATA)
    setFinalReport(null)
    setPivotSuggestions(null)
    setError(null)
    setResetKey(k => k + 1)

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea }),
      })
      if (!res.ok) {
        const body = await res.json()
        throw new Error(body.detail || 'Server error')
      }
      const { run_id } = await res.json()
      runIdRef.current = run_id
      connect(run_id)
    } catch (err) {
      setError(err.message)
      setPhase('idle')
    }
  }

  const handleDownload = () => {
    if (!runIdRef.current) return
    window.open(`/api/report/${runIdRef.current}/pdf`, '_blank')
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC]">

      {/* ── Header ── */}
      <header className="bg-white border-b border-slate-100 sticky top-0 z-50 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-md">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-sm font-bold text-slate-900 tracking-tight">VentureIQ</h1>
              <p className="text-[10px] text-slate-400 font-medium">Multi-Agent AI Analysis</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {phase === 'running' && (
              <motion.span
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="flex items-center gap-1.5 text-xs text-blue-600 font-semibold bg-blue-50 border border-blue-100 px-3 py-1.5 rounded-full"
              >
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-ping" />
                Analyzing...
              </motion.span>
            )}
            {phase === 'done' && (
              <span className="flex items-center gap-1.5 text-xs text-emerald-600 font-semibold bg-emerald-50 border border-emerald-100 px-3 py-1.5 rounded-full">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                Analysis Complete
              </span>
            )}
            {phase === 'idle' && (
              <span className="flex items-center gap-1.5 text-xs text-slate-500 bg-slate-50 border border-slate-100 px-3 py-1.5 rounded-full">
                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full" />
                Ready
              </span>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-12 space-y-12">

        {/* ── Hero ── */}
        <AnimatePresence>
          {phase === 'idle' && (
            <motion.div
              initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.4 }}
              className="text-center space-y-6"
            >
              <div className="inline-flex items-center gap-2 bg-blue-50 border border-blue-100 text-blue-600 text-xs font-semibold px-4 py-1.5 rounded-full">
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
                Powered by LangGraph Multi-Agent Pipeline
              </div>
              <div className="space-y-3">
                <h2 className="text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
                  Should you build<br />
                  <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    this startup?
                  </span>
                </h2>
                <p className="text-slate-500 text-lg max-w-lg mx-auto leading-relaxed">
                  <span className="font-semibold text-slate-700">VentureIQ</span> deploys 7 specialized AI agents to analyze your idea across market, competition, financials, and risk — in under 60 seconds.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3">
                {STATS.map((s, i) => (
                  <motion.span
                    key={i}
                    initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * i }}
                    className="flex items-center gap-2 bg-white border border-slate-200 text-slate-600 text-xs font-medium px-4 py-2 rounded-full shadow-sm"
                  >
                    <span>{s.icon}</span> {s.label}
                  </motion.span>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Input ── */}
        <IdeaInput onSubmit={handleSubmit} isLoading={phase === 'running'} />

        {/* ── Error ── */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="flex items-center gap-3 bg-rose-50 border border-rose-200 text-rose-700 text-sm px-5 py-3.5 rounded-2xl"
            >
              <span className="text-rose-500">⚠</span> {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Analysis ── */}
        <AnimatePresence>
          {phase !== 'idle' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="space-y-8"
            >
              {/* Agent Pipeline */}
              <Section label="Agent Pipeline">
                <AgentGraph agentStatuses={agentStatuses} resetKey={resetKey} />
              </Section>

              {/* Agent Outputs */}
              <Section label="Agent Outputs">
                <StreamingPanel agentStatuses={agentStatuses} agentData={agentData} />
              </Section>

              {/* Final Verdict */}
              <AnimatePresence>
                {finalReport && (
                  <Section label="Final Verdict">
                    <VerdictCard
                      report={finalReport}
                      pivots={pivotSuggestions}
                      financialData={agentData?.financial_feasibility}
                      onDownload={handleDownload}
                    />
                  </Section>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>

        {phase === 'idle' && (
          <p className="text-center text-xs text-slate-400 pb-4">
            Results are indicative — not financial advice. Validate with real customers.
          </p>
        )}
      </main>

      {/* Floating Chat Widget — appears after verdict */}
      <AnimatePresence>
        {finalReport && runIdRef.current && (
          <ChatWidget runId={runIdRef.current} />
        )}
      </AnimatePresence>
    </div>
  )
}

function Section({ label, children }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">{label}</span>
        <div className="flex-1 h-px bg-slate-100" />
      </div>
      {children}
    </div>
  )
}
