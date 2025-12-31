'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { TrendingUp, CheckCircle, AlertCircle, Download, PieChart, ChevronDown, ChevronUp } from 'lucide-react'
import { EmissionCalculationResponse } from '@/services/api'
import ReportGenerator from './ReportGenerator'
import { useMemo } from 'react'

interface ResultsDisplayProps {
  results: EmissionCalculationResponse | null
}

export default function ResultsDisplay({ results }: ResultsDisplayProps) {
  const [detailedExpanded, setDetailedExpanded] = useState(false)
  
  if (!results) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="glass rounded-2xl p-8 shadow-xl"
      >
        <div className="text-center text-sage-500">
          <TrendingUp className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg">Enter your energy consumption data to calculate emissions</p>
        </div>
      </motion.div>
    )
  }

  // Debug: Log results to console
  console.log('ResultsDisplay received:', results)
  
  // Validate results structure
  if (!results.results || !Array.isArray(results.results) || results.results.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="glass rounded-2xl p-8 shadow-xl"
      >
        <div className="text-center text-red-500">
          <AlertCircle className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg">No results found in response</p>
          <p className="text-sm mt-2">Please check the console for details</p>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass rounded-2xl p-8 shadow-xl space-y-6"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-forest-100 rounded-lg">
          <CheckCircle className="w-6 h-6 text-forest-600" />
        </div>
        <h2 className="text-2xl font-display text-forest-700">Results</h2>
      </div>

      {/* Total Emissions */}
      <div className="bg-gradient-to-br from-forest-50 to-sage-50 rounded-xl p-6 border border-forest-100">
        <div className="text-sm text-sage-600 mb-2">Total CO₂ Equivalent</div>
        <div className="text-4xl font-display text-forest-700 mb-1">
          {(results.total_co2e_ton || 0).toFixed(2)}
        </div>
        <div className="text-sm text-sage-500">tons ({(results.total_co2e_kg || 0).toFixed(2)} kg)</div>
      </div>

      {/* Scope Summary with Visual Chart */}
      {results.scope_summary && Object.keys(results.scope_summary).length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <PieChart className="w-5 h-5 text-forest-600" />
            <h3 className="text-lg font-semibold text-forest-700">Scope Breakdown</h3>
          </div>
          
          {/* Visual Bar Chart */}
          <div className="mb-4 p-4 bg-white rounded-lg border border-sage-100">
            {(() => {
              const total = Object.values(results.scope_summary).reduce((a, b) => (a as number) + (b as number), 0) as number
              const colors: Record<string, string> = {
                'Scope 1': 'bg-forest-500',
                'Scope 2': 'bg-sage-500', 
                'Scope 3': 'bg-blue-500',
                'Unknown': 'bg-gray-400'
              }
              return (
                <div className="space-y-3">
                  {Object.entries(results.scope_summary).map(([scope, value]) => {
                    const percentage = total > 0 ? ((value as number) / total) * 100 : 0
                    return (
                      <div key={scope} className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span className="font-medium text-sage-700">{scope}</span>
                          <span className="text-forest-600">{percentage.toFixed(1)}% ({(value as number).toFixed(2)} t)</span>
                        </div>
                        <div className="h-3 bg-sage-100 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${percentage}%` }}
                            transition={{ duration: 0.8, delay: 0.2 }}
                            className={`h-full ${colors[scope] || colors['Unknown']} rounded-full`}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>
              )
            })()}
          </div>

          <div className="space-y-3">
            {Object.entries(results.scope_summary).map(([scope, value], index) => (
              <motion.div
                key={scope}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-4 bg-white rounded-lg border border-sage-100"
              >
                <span className="font-medium text-sage-700">{scope}</span>
                <span className="text-forest-600 font-semibold">{(value as number).toFixed(2)} tons</span>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Results - Collapsible */}
      <div className="pt-4 border-t border-sage-200">
        <button
          onClick={() => setDetailedExpanded(!detailedExpanded)}
          className="flex items-center justify-between w-full mb-3 text-sm font-semibold text-sage-600 hover:text-forest-700 transition-colors"
        >
          <span>Detaylı Sonuçlar ({results.results.length} aktivite)</span>
          {detailedExpanded ? (
            <ChevronUp className="w-5 h-5" />
          ) : (
            <ChevronDown className="w-5 h-5" />
          )}
        </button>
        <AnimatePresence>
          {detailedExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
          {results.results.map((result, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.02 }}
              className="p-4 bg-white rounded-lg border border-sage-100"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sage-700">{result.activity_name}</span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  result.source?.toLowerCase().includes('climatiq') ? 'bg-blue-100 text-blue-700' :
                  result.source?.toLowerCase().includes('epa') ? 'bg-green-100 text-green-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {result.source || 'Unknown'}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs text-sage-600">
                <div>
                        <span className="font-medium">Miktar:</span> {result.amount} {result.unit}
                </div>
                <div>
                        <span className="font-medium">CO₂e:</span> {result.co2e_ton.toFixed(3)} ton
                </div>
                <div>
                  <span className="font-medium">Scope:</span> {result.scope}
                </div>
                <div>
                        <span className="font-medium">Kategori:</span> {result.category}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Export Actions */}
      <div className="pt-4 border-t border-sage-200">
        <h3 className="text-sm font-semibold text-sage-600 mb-3">Export Data</h3>
        <div className="flex gap-3">
          <button
            onClick={() => {
              const exportData = {
                timestamp: new Date().toISOString(),
                total_co2e_ton: results.total_co2e_ton,
                total_co2e_kg: results.total_co2e_kg,
                scope_summary: results.scope_summary,
                results: results.results.map(r => ({
                  activity_name: r.activity_name,
                  amount: r.amount,
                  unit: r.unit,
                  co2e_kg: r.co2e_kg,
                  co2e_ton: r.co2e_ton,
                  scope: r.scope,
                  category: r.category,
                  region: r.region,
                  source: r.source
                }))
              }
              const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `emission_results_${new Date().toISOString().split('T')[0]}.json`
              document.body.appendChild(a)
              a.click()
              document.body.removeChild(a)
              URL.revokeObjectURL(url)
            }}
            className="flex items-center gap-2 px-4 py-2 bg-sage-100 hover:bg-sage-200 text-sage-700 font-medium rounded-lg transition-all"
          >
            <Download className="w-4 h-4" />
            Export JSON
          </button>
          <button
            onClick={() => {
              // CSV export
              const headers = ['Activity', 'Amount', 'Unit', 'CO2e (kg)', 'CO2e (ton)', 'Scope', 'Category', 'Region', 'Source']
              const rows = results.results.map(r => [
                r.activity_name,
                r.amount,
                r.unit,
                r.co2e_kg,
                r.co2e_ton,
                r.scope,
                r.category,
                r.region,
                r.source
              ])
              const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
              const blob = new Blob([csvContent], { type: 'text/csv' })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `emission_results_${new Date().toISOString().split('T')[0]}.csv`
              document.body.appendChild(a)
              a.click()
              document.body.removeChild(a)
              URL.revokeObjectURL(url)
            }}
            className="flex items-center gap-2 px-4 py-2 bg-sage-100 hover:bg-sage-200 text-sage-700 font-medium rounded-lg transition-all"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Report Generator */}
      <ReportGenerator results={results} />
    </motion.div>
  )
}

