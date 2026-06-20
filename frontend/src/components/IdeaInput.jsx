import { useState } from 'react'
import { motion } from 'framer-motion'

const EXAMPLES = [
  'An AI-powered WhatsApp tutoring bot for Class 10-12 students in India that instantly solves doubts in Math and Science in Hindi. Students pay ₹199/month.',
  'A SaaS platform for small Indian restaurants to manage digital menus, take WhatsApp orders, and track daily sales via QR code. ₹299/month per restaurant.',
  'An AI vernacular job portal for blue-collar workers in India where job seekers create voice profiles in local languages instead of resumes. Employers pay ₹499 per hire.',
]

export default function IdeaInput({ onSubmit, isLoading }) {
  const [idea, setIdea]   = useState('')
  const [focused, setFocused] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (idea.trim().length >= 20 && !isLoading) onSubmit(idea.trim())
  }

  const charPct = (idea.length / 2000) * 100

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-3">

        {/* Textarea card */}
        <div className={`relative bg-white rounded-2xl border-2 shadow-sm transition-all duration-200 ${
          focused ? 'border-blue-400 shadow-blue-50 shadow-md' : 'border-slate-200'
        }`}>
          <textarea
            value={idea}
            onChange={e => setIdea(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Describe your startup idea in detail — include the target customer, problem being solved, revenue model, and geography..."
            rows={5}
            maxLength={2000}
            disabled={isLoading}
            className="w-full resize-none bg-transparent px-5 pt-4 pb-10 text-slate-800 placeholder-slate-400 text-sm leading-relaxed focus:outline-none disabled:opacity-50"
          />
          {/* Bottom bar */}
          <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between px-5 pb-3">
            <div className="flex items-center gap-1.5">
              <div className="w-24 h-1 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-300 ${charPct > 80 ? 'bg-amber-400' : 'bg-blue-400'}`}
                  style={{ width: `${charPct}%` }}
                />
              </div>
              <span className="text-[11px] text-slate-400">{idea.length}/2000</span>
            </div>
            {idea.length >= 20 && !isLoading && (
              <motion.span
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="text-[11px] text-emerald-600 font-medium"
              >
                ✓ Ready to analyze
              </motion.span>
            )}
          </div>
        </div>

        {/* Row: examples + button */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[11px] text-slate-400 font-medium">Try:</span>
            {EXAMPLES.map((ex, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setIdea(ex)}
                disabled={isLoading}
                className="text-[11px] text-blue-600 bg-blue-50 hover:bg-blue-100 border border-blue-100 rounded-full px-3 py-1 transition-all disabled:opacity-40 font-medium"
              >
                Example {i + 1}
              </button>
            ))}
          </div>

          <motion.button
            type="submit"
            disabled={idea.trim().length < 20 || isLoading}
            whileTap={{ scale: 0.97 }}
            className="shrink-0 flex items-center gap-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-slate-300 disabled:to-slate-300 text-white font-semibold text-sm px-6 py-2.5 rounded-xl shadow-md shadow-blue-100 transition-all duration-200 disabled:cursor-not-allowed disabled:shadow-none"
          >
            {isLoading ? (
              <>
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Analyze Idea
              </>
            )}
          </motion.button>
        </div>
      </form>
    </div>
  )
}
