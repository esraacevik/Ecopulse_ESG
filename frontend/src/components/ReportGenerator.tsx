'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, Download, Loader2, CheckCircle2, Circle, AlertCircle } from 'lucide-react'
import { reportAPI, ReportProgressMessage } from '@/services/api'
import { EmissionCalculationResponse } from '@/services/api'

interface ReportGeneratorProps {
  results: EmissionCalculationResponse | null
  companyName?: string
  period?: string
}

interface ReportStep {
  id: string
  label: string
  step: string
  completed: boolean
  inProgress: boolean
}

export default function ReportGenerator({ results, companyName: initialCompanyName = "Company", period: initialPeriod = "2024 Q1" }: ReportGeneratorProps) {
  const [companyName, setCompanyName] = useState(initialCompanyName)
  const [period, setPeriod] = useState(initialPeriod)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [currentMessage, setCurrentMessage] = useState<string | null>(null)
  const [steps, setSteps] = useState<ReportStep[]>([
    { id: 'cover', label: 'Kapak Sayfası', step: 'cover', completed: false, inProgress: false },
    { id: 'executive_summary', label: 'Yönetici Özeti', step: 'executive_summary', completed: false, inProgress: false },
    { id: 'emission_summary', label: 'Emisyon Özeti', step: 'emission_summary', completed: false, inProgress: false },
    { id: 'charts', label: 'Görselleştirmeler', step: 'charts', completed: false, inProgress: false },
    { id: 'ai_content', label: 'AI İçerik Üretimi', step: 'ai_content', completed: false, inProgress: false },
    { id: 'detailed_data', label: 'Detaylı Veriler', step: 'detailed_data', completed: false, inProgress: false },
    { id: 'performance', label: 'Performans Analizi', step: 'performance', completed: false, inProgress: false },
    { id: 'critical_analysis', label: 'Kritik Analiz', step: 'critical_analysis', completed: false, inProgress: false },
    { id: 'recommendations', label: 'Öneriler', step: 'recommendations', completed: false, inProgress: false },
    { id: 'risk', label: 'Risk Analizi', step: 'risk', completed: false, inProgress: false },
    { id: 'methodology', label: 'Metodoloji', step: 'methodology', completed: false, inProgress: false },
    { id: 'closing', label: 'Kapanış', step: 'closing', completed: false, inProgress: false },
    { id: 'pdf_generation', label: 'PDF Oluşturma', step: 'pdf_generation', completed: false, inProgress: false },
  ])

  const updateStep = (stepId: string, completed: boolean, inProgress: boolean) => {
    setSteps(prev => prev.map(s => 
      s.step === stepId 
        ? { ...s, completed, inProgress }
        : { ...s, inProgress: false }
    ))
  }

  const generateReport = async () => {
    if (!results) {
      setError("Hesaplama sonuçları bulunamadı")
      return
    }

    setLoading(true)
    setError(null)
    setDownloadUrl(null)
    setProgress(0)
    setCurrentMessage(null)
    setSteps(prev => prev.map(s => ({ ...s, completed: false, inProgress: false })))

    try {
      // Safe filename (no Turkish characters for URL)
      const safeCompanyName = companyName
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // Remove diacritics
        .replace(/[^\w\s-]/g, '') // Remove special chars
        .replace(/\s+/g, '_') // Spaces to underscores
        .toLowerCase()
      
      const filename = await reportAPI.generateStream(
        {
          results: results.results,
          company_name: companyName,
          period: period,
          filename: `esg_report_${safeCompanyName}_${new Date().toISOString().split('T')[0]}.pdf`
        },
        (message: ReportProgressMessage) => {
          // Update progress
          if (message.percentage !== undefined) {
            setProgress(message.percentage)
          }

          // Update current message
          if (message.message) {
            setCurrentMessage(message.message)
          }

          // Update steps
          if (message.step) {
            if (message.type === 'progress') {
              updateStep(message.step, false, true)
            } else if (message.type === 'complete' && message.step === 'complete') {
              // All steps completed
              setSteps(prev => prev.map(s => ({ ...s, completed: true, inProgress: false })))
            }
          }

          // Mark step as completed when moving to next
          if (message.step && message.type === 'progress') {
            // Find current step and mark previous as completed
            const currentStepIndex = steps.findIndex(s => s.step === message.step)
            if (currentStepIndex > 0) {
              const prevStep = steps[currentStepIndex - 1]
              updateStep(prevStep.step, true, false)
            }
          }
        }
      )

      // Report completed
      const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/report/download/${filename}`
      setDownloadUrl(url)
      setProgress(100)
      setCurrentMessage("Rapor başarıyla oluşturuldu!")
      setSteps(prev => prev.map(s => ({ ...s, completed: true, inProgress: false })))
    } catch (err: any) {
      setError(err.message || 'Rapor oluşturma başarısız oldu')
      setProgress(0)
      setCurrentMessage(null)
    } finally {
      setLoading(false)
    }
  }

  if (!results) {
    return null
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-6"
    >
      <div className="glass rounded-xl p-6 border border-forest-100">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-forest-100 rounded-lg">
            <FileText className="w-5 h-5 text-forest-600" />
          </div>
          <h3 className="text-lg font-semibold text-forest-700">ESG Rapor Oluştur</h3>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">Şirket Adı</label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="w-full px-4 py-2 rounded-lg border border-sage-200 focus:border-forest-500 focus:ring-2 focus:ring-forest-200 focus:outline-none"
                placeholder="Şirket Adı"
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">Dönem</label>
              <input
                type="text"
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="w-full px-4 py-2 rounded-lg border border-sage-200 focus:border-forest-500 focus:ring-2 focus:ring-forest-200 focus:outline-none"
                placeholder="Dönem (örn: 2024 Yıllık)"
                disabled={loading}
              />
            </div>
          </div>

          {/* Progress Section */}
          {loading && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-4"
            >
              {/* Progress Bar */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-forest-700 font-medium">İlerleme</span>
                  <span className="text-forest-600">{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <motion.div
                    className="bg-green-600 h-2.5 rounded-full transition-all duration-300"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                  />
                </div>
              </div>

              {/* Current Message */}
              {currentMessage && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-700 text-sm"
                >
                  {currentMessage}
                </motion.div>
              )}

              {/* Steps List */}
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {steps.map((step, index) => (
                  <motion.div
                    key={step.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-center gap-3 text-sm"
                  >
                    {step.completed ? (
                      <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
                    ) : step.inProgress ? (
                      <Loader2 className="w-5 h-5 text-blue-600 animate-spin flex-shrink-0" />
                    ) : (
                      <Circle className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    )}
                    <span
                      className={
                        step.completed
                          ? 'text-gray-600 line-through'
                          : step.inProgress
                          ? 'text-blue-700 font-medium'
                          : 'text-gray-400'
                      }
                    >
                      {step.label}
                    </span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center gap-2"
            >
              <AlertCircle className="w-5 h-5" />
              {error}
            </motion.div>
          )}

          {downloadUrl ? (
            <motion.button
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              onClick={async () => {
                try {
                  // Fetch PDF as blob
                  const response = await fetch(downloadUrl)
                  if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`)
                  }
                  
                  const blob = await response.blob()
                  const url = window.URL.createObjectURL(blob)
                  const link = document.createElement('a')
                  link.href = url
                  link.download = downloadUrl.split('/').pop() || 'esg_report.pdf'
                  document.body.appendChild(link)
                  link.click()
                  document.body.removeChild(link)
                  window.URL.revokeObjectURL(url)
                } catch (err: any) {
                  setError(`İndirme hatası: ${err.message}`)
                }
              }}
              className="flex items-center justify-center gap-2 w-full py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-all"
            >
              <Download className="w-5 h-5" />
              PDF Raporu İndir
            </motion.button>
          ) : (
            <button
              onClick={generateReport}
              disabled={loading}
              className="w-full py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Rapor Oluşturuluyor...
                </>
              ) : (
                <>
                  <FileText className="w-5 h-5" />
                  PDF Rapor Oluştur
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </motion.div>
  )
}
