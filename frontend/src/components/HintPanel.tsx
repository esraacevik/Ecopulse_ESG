'use client'

import { Lightbulb, HelpCircle, CheckCircle, Info } from 'lucide-react'

interface HintPanelProps {
  title: string
  hints: string[]
  tips?: string[]
  variant?: 'default' | 'success' | 'info'
}

export default function HintPanel({ title, hints, tips, variant = 'default' }: HintPanelProps) {
  const variants = {
    default: {
      bg: 'from-sage-50 to-white',
      border: 'border-sage-200',
      iconBg: 'bg-forest-100',
      icon: 'text-forest-600',
      title: 'text-forest-700'
    },
    success: {
      bg: 'from-green-50 to-white',
      border: 'border-green-200',
      iconBg: 'bg-green-100',
      icon: 'text-green-600',
      title: 'text-green-700'
    },
    info: {
      bg: 'from-blue-50 to-white',
      border: 'border-blue-200',
      iconBg: 'bg-blue-100',
      icon: 'text-blue-600',
      title: 'text-blue-700'
    }
  }

  const v = variants[variant]

  return (
    <div className={`bg-gradient-to-br ${v.bg} rounded-xl p-4 border ${v.border}`}>
      <div className="flex items-center gap-2 mb-3">
        <div className={`p-1.5 ${v.iconBg} rounded-lg`}>
          <Lightbulb className={`w-4 h-4 ${v.icon}`} />
        </div>
        <h4 className={`font-semibold ${v.title} text-sm`}>{title}</h4>
      </div>
      
      <ul className="space-y-2 text-sm text-sage-600">
        {hints.map((hint, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="text-forest-500 mt-0.5">•</span>
            <span>{hint}</span>
          </li>
        ))}
      </ul>
      
      {tips && tips.length > 0 && (
        <div className="mt-3 pt-3 border-t border-sage-200">
          <div className="flex items-center gap-1 text-xs text-amber-600 mb-2">
            <HelpCircle className="w-3 h-3" />
            <span className="font-medium">İpucu</span>
          </div>
          {tips.map((tip, i) => (
            <p key={i} className="text-xs text-sage-500 italic">{tip}</p>
          ))}
        </div>
      )}
    </div>
  )
}

// Quick tips component for simpler hints
export function QuickTip({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-start gap-2 p-3 bg-amber-50 rounded-lg border border-amber-200">
      <Info className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
      <p className="text-sm text-amber-800">{children}</p>
    </div>
  )
}

// Standards badge component
export function StandardsBadge({ standards }: { standards: string[] }) {
  return (
    <div className="bg-gradient-to-br from-forest-50 to-forest-100 rounded-xl p-4 border border-forest-200">
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 bg-forest-500 rounded-lg">
          <CheckCircle className="w-4 h-4 text-white" />
        </div>
        <h4 className="font-semibold text-forest-700 text-sm">Desteklenen Standartlar</h4>
      </div>
      <div className="flex flex-wrap gap-2">
        {standards.map((std, i) => (
          <span key={i} className="text-xs px-2 py-1 bg-white rounded-full text-forest-700">
            {std}
          </span>
        ))}
      </div>
    </div>
  )
}

