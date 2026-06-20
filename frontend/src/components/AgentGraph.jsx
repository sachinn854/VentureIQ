import ReactFlow, { Handle, Position, Background, useNodesState, useEdgesState } from 'reactflow'
import { useEffect } from 'react'

const STATUS_CONFIG = {
  idle:     { ring: 'border-slate-200',  bg: 'bg-white',       text: 'text-slate-400', dot: 'bg-slate-300' },
  running:  { ring: 'border-blue-400',   bg: 'bg-blue-50',     text: 'text-blue-600',  dot: 'bg-blue-500 animate-ping' },
  complete: { ring: 'border-emerald-400',bg: 'bg-emerald-50',  text: 'text-emerald-700',dot: 'bg-emerald-500' },
  error:    { ring: 'border-rose-400',   bg: 'bg-rose-50',     text: 'text-rose-600',  dot: 'bg-rose-500' },
}

const AGENT_META = {
  input_processor:     { label: 'Input Processor',    icon: '⚙️' },
  market_research:     { label: 'Market Research',    icon: '📊' },
  competitor_analysis: { label: 'Competitors',        icon: '🔍' },
  financial_feasibility:{ label: 'Financials',        icon: '💰' },
  risk_assessment:     { label: 'Risk Assessment',    icon: '⚠️' },
  synthesizer:         { label: 'Synthesizer',        icon: '🧠' },
  pivot_advisor:       { label: 'Pivot Advisor',      icon: '🔄' },
}

function AgentNode({ data }) {
  const cfg = STATUS_CONFIG[data.status] || STATUS_CONFIG.idle
  const meta = AGENT_META[data.id] || { label: data.label, icon: '○' }

  return (
    <div className={`border-2 rounded-2xl px-3 py-2 min-w-[130px] shadow-sm transition-all duration-300 ${cfg.ring} ${cfg.bg}`}>
      <Handle type="target" position={Position.Top} style={{ background: '#CBD5E1', border: 'none', width: 6, height: 6 }} />
      <div className="flex items-center gap-2">
        <span className="text-sm">{meta.icon}</span>
        <span className={`text-[11px] font-semibold leading-tight ${cfg.text}`}>{meta.label}</span>
        <span className={`ml-auto w-2 h-2 rounded-full shrink-0 ${cfg.dot}`} />
      </div>
      <Handle type="source" position={Position.Bottom} style={{ background: '#CBD5E1', border: 'none', width: 6, height: 6 }} />
    </div>
  )
}

const nodeTypes = { agentNode: AgentNode }

const INITIAL_NODES = [
  { id: 'input_processor',      type: 'agentNode', position: { x: 210, y: 0   }, data: { id: 'input_processor',      label: 'Input Processor', status: 'idle' } },
  { id: 'market_research',      type: 'agentNode', position: { x: 0,   y: 110 }, data: { id: 'market_research',      label: 'Market Research', status: 'idle' } },
  { id: 'competitor_analysis',  type: 'agentNode', position: { x: 155, y: 110 }, data: { id: 'competitor_analysis',  label: 'Competitors',     status: 'idle' } },
  { id: 'financial_feasibility',type: 'agentNode', position: { x: 320, y: 110 }, data: { id: 'financial_feasibility',label: 'Financials',      status: 'idle' } },
  { id: 'risk_assessment',      type: 'agentNode', position: { x: 475, y: 110 }, data: { id: 'risk_assessment',      label: 'Risk Assessment', status: 'idle' } },
  { id: 'synthesizer',          type: 'agentNode', position: { x: 210, y: 220 }, data: { id: 'synthesizer',          label: 'Synthesizer',     status: 'idle' } },
]

const INITIAL_EDGES = [
  { id: 'e1', source: 'input_processor', target: 'market_research',       animated: false, style: { stroke: '#E2E8F0', strokeWidth: 2 } },
  { id: 'e2', source: 'input_processor', target: 'competitor_analysis',   animated: false, style: { stroke: '#E2E8F0', strokeWidth: 2 } },
  { id: 'e3', source: 'input_processor', target: 'financial_feasibility', animated: false, style: { stroke: '#E2E8F0', strokeWidth: 2 } },
  { id: 'e4', source: 'input_processor', target: 'risk_assessment',       animated: false, style: { stroke: '#E2E8F0', strokeWidth: 2 } },
  { id: 'e5', source: 'market_research',       target: 'synthesizer',     animated: false, style: { stroke: '#E2E8F0', strokeWidth: 2 } },
  { id: 'e6', source: 'competitor_analysis',   target: 'synthesizer',     animated: false, style: { stroke: '#E2E8F0', strokeWidth: 2 } },
  { id: 'e7', source: 'financial_feasibility', target: 'synthesizer',     animated: false, style: { stroke: '#E2E8F0', strokeWidth: 2 } },
  { id: 'e8', source: 'risk_assessment',       target: 'synthesizer',     animated: false, style: { stroke: '#E2E8F0', strokeWidth: 2 } },
]

export default function AgentGraph({ agentStatuses, resetKey }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(INITIAL_NODES)
  const [edges, setEdges, onEdgesChange] = useEdgesState(INITIAL_EDGES)

  useEffect(() => {
    setNodes(INITIAL_NODES.map(n => ({ ...n, data: { ...n.data, status: 'idle' } })))
    setEdges(INITIAL_EDGES.map(e => ({ ...e, animated: false, style: { stroke: '#E2E8F0', strokeWidth: 2 } })))
  }, [resetKey])

  useEffect(() => {
    setNodes(prev => prev.map(n => ({
      ...n, data: { ...n.data, status: agentStatuses[n.id] || 'idle' }
    })))
    setEdges(prev => prev.map(e => {
      const s = agentStatuses[e.source]
      const active = s === 'running' || s === 'complete'
      return { ...e, animated: active, style: { stroke: active ? '#3B82F6' : '#E2E8F0', strokeWidth: active ? 2.5 : 2 } }
    }))
  }, [agentStatuses])

  return (
    <div className="w-full h-72 rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <ReactFlow
        nodes={nodes} edges={edges}
        onNodesChange={onNodesChange} onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView fitViewOptions={{ padding: 0.3 }}
        nodesDraggable={false} nodesConnectable={false}
        elementsSelectable={false} zoomOnScroll={false} panOnDrag={false}
      >
        <Background color="#F1F5F9" gap={20} size={1} />
      </ReactFlow>
    </div>
  )
}
