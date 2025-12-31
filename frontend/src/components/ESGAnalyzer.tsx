'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  FileText, 
  Upload, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Leaf,
  Users,
  Building2,
  TrendingUp,
  FileSearch,
  Zap,
  Target,
  Shield,
  Award,
  ThermometerSun,
  BarChart3
} from 'lucide-react'
import { analyzerAPI, ESGAnalysisResponse } from '@/services/api'

type AnalysisMode = 'text' | 'pdf'

export default function ESGAnalyzer() {
  const [mode, setMode] = useState<AnalysisMode>('text')
  const [inputText, setInputText] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<ESGAnalysisResponse | null>(null)

  const handleTextAnalysis = async () => {
    if (!inputText.trim()) {
      setError('Lütfen analiz edilecek metin girin')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const response = await analyzerAPI.analyzeText(inputText)
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analiz sırasında hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  const handlePDFAnalysis = async () => {
    if (!selectedFile) {
      setError('Lütfen bir PDF dosyası seçin')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const response = await analyzerAPI.analyzePDF(selectedFile)
      setResults(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'PDF analizi sırasında hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('Sadece PDF dosyaları kabul edilir')
        return
      }
      setSelectedFile(file)
      setError(null)
    }
  }

  const getRiskColor = (score: number) => {
    if (score < 30) return 'text-green-600'
    if (score < 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getRiskBgColor = (score: number) => {
    if (score < 30) return 'bg-green-100 border-green-300'
    if (score < 60) return 'bg-yellow-100 border-yellow-300'
    return 'bg-red-100 border-red-300'
  }

  const getRiskLevel = (score: number) => {
    if (score < 20) return 'Düşük Risk'
    if (score < 40) return 'Orta-Düşük Risk'
    if (score < 60) return 'Orta Risk'
    if (score < 80) return 'Orta-Yüksek Risk'
    return 'Yüksek Risk'
  }

  const getSentimentEmoji = (label?: string) => {
    if (label === 'Pozitif') return '😊'
    if (label === 'Negatif') return '😟'
    return '😐'
  }

  const getSentimentColor = (label?: string) => {
    if (label === 'Pozitif') return 'text-green-600 bg-green-50'
    if (label === 'Negatif') return 'text-red-600 bg-red-50'
    return 'text-gray-600 bg-gray-50'
  }

  // ESG classification artık yüzde olarak geliyor (0-100)
  const getESGBarWidth = (value: number) => `${Math.min(value, 100)}%`

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-6 shadow-xl"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-forest-100 rounded-lg">
            <FileSearch className="w-6 h-6 text-forest-600" />
          </div>
          <div>
            <h2 className="text-2xl font-display text-forest-700">ESG Analyzer v2</h2>
            <p className="text-sm text-sage-600">Gelişmiş ESG rapor ve metin analizi</p>
          </div>
        </div>

        {/* Mode Toggle */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => { setMode('text'); setResults(null); setError(null); }}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
              mode === 'text' 
                ? 'bg-forest-600 text-white' 
                : 'bg-sage-100 text-sage-700 hover:bg-sage-200'
            }`}
          >
            <FileText className="w-5 h-5" />
            Metin Analizi
          </button>
          <button
            onClick={() => { setMode('pdf'); setResults(null); setError(null); }}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
              mode === 'pdf' 
                ? 'bg-forest-600 text-white' 
                : 'bg-sage-100 text-sage-700 hover:bg-sage-200'
            }`}
          >
            <Upload className="w-5 h-5" />
            PDF Analizi
          </button>
        </div>

        {/* Input Area */}
        <AnimatePresence mode="wait">
          {mode === 'text' ? (
            <motion.div
              key="text"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-4"
            >
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="ESG raporu metnini buraya yapıştırın...

Örnek içerik:
- Scope 1, 2, 3 emisyonları
- Karbon ayak izi verileri
- Sürdürülebilirlik hedefleri
- Çalışan sağlık ve güvenlik bilgileri
- Yönetim kurulu yapısı"
                className="w-full h-48 p-4 rounded-lg border border-sage-300 focus:border-forest-500 focus:ring-2 focus:ring-forest-200 resize-none transition-all"
              />
              <button
                onClick={handleTextAnalysis}
                disabled={loading || !inputText.trim()}
                className="w-full py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
                    Analiz Ediliyor...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    Metni Analiz Et
                  </>
                )}
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="pdf"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <div className="border-2 border-dashed border-sage-300 rounded-lg p-8 text-center hover:border-forest-400 transition-all">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="pdf-upload"
                />
                <label htmlFor="pdf-upload" className="cursor-pointer">
                  <Upload className="w-12 h-12 mx-auto mb-4 text-sage-400" />
                  {selectedFile ? (
                    <div>
                      <p className="text-lg font-semibold text-forest-700">{selectedFile.name}</p>
                      <p className="text-sm text-sage-500">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-lg font-semibold text-sage-700">PDF dosyası seçin</p>
                      <p className="text-sm text-sage-500">veya sürükleyip bırakın</p>
                    </div>
                  )}
                </label>
              </div>
              <button
                onClick={handlePDFAnalysis}
                disabled={loading || !selectedFile}
                className="w-full py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
                    PDF Analiz Ediliyor...
                  </>
                ) : (
                  <>
                    <FileSearch className="w-5 h-5" />
                    PDF'i Analiz Et
                  </>
                )}
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700"
          >
            <XCircle className="w-5 h-5 flex-shrink-0" />
            {error}
          </motion.div>
        )}
      </motion.div>

      {/* Results */}
      <AnimatePresence>
        {results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Risk Score Card with Details */}
            <div className={`glass rounded-2xl p-6 shadow-xl border-2 ${getRiskBgColor(results.risk_score)}`}>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-sage-700 flex items-center gap-2">
                    <Shield className="w-5 h-5" />
                    Risk Değerlendirmesi
                  </h3>
                  <p className="text-sm text-sage-500">{getRiskLevel(results.risk_score)}</p>
                </div>
                <div className="text-center">
                  <div className={`text-5xl font-bold ${getRiskColor(results.risk_score)}`}>
                    {results.risk_score}
                  </div>
                  <div className="text-sm text-sage-500">/100</div>
                </div>
              </div>
              
              {/* Risk Components */}
              {results.risk_details && (
                <div className="grid grid-cols-5 gap-2 pt-4 border-t border-sage-200">
                  {Object.entries(results.risk_details.components || {}).map(([key, value]) => (
                    <div key={key} className="text-center p-2 bg-white/50 rounded-lg">
                      <div className="text-lg font-bold text-sage-700">{value as number}</div>
                      <div className="text-xs text-sage-500 capitalize">
                        {key.replace(/_/g, ' ')}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Sentiment & Confidence Row */}
            <div className="grid grid-cols-2 gap-4">
              {/* Sentiment */}
              {results.sentiment && (
                <div className={`glass rounded-2xl p-4 shadow-xl ${getSentimentColor(results.sentiment.label)}`}>
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{getSentimentEmoji(results.sentiment.label)}</span>
                    <div>
                      <h4 className="font-semibold">Genel Ton</h4>
                      <p className="text-sm">{results.sentiment.label} ({results.sentiment.score})</p>
                    </div>
                  </div>
                  {(results.sentiment.high_risk_count > 0 || results.sentiment.positive_indicators > 0) && (
                    <div className="mt-2 pt-2 border-t border-current/20 text-sm">
                      {results.sentiment.positive_indicators > 0 && (
                        <span className="mr-3">✅ {results.sentiment.positive_indicators} pozitif</span>
                      )}
                      {results.sentiment.high_risk_count > 0 && (
                        <span className="text-red-600">⚠️ {results.sentiment.high_risk_count} risk</span>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Confidence */}
              {results.confidence && (
                <div className="glass rounded-2xl p-4 shadow-xl bg-blue-50">
                  <div className="flex items-center gap-3">
                    <BarChart3 className="w-8 h-8 text-blue-600" />
                    <div>
                      <h4 className="font-semibold text-blue-800">Analiz Güveni</h4>
                      <p className="text-sm text-blue-600">{results.confidence.level} ({results.confidence.score}%)</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Targets */}
            {results.targets && (results.targets.net_zero || (results.targets.certifications?.length || 0) > 0) && (
              <div className="glass rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-semibold text-forest-700 mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Hedefler ve Sertifikalar
                </h3>
                <div className="flex flex-wrap gap-3">
                  {results.targets.net_zero && (
                    <div className="px-4 py-2 bg-green-100 text-green-800 rounded-full font-medium flex items-center gap-2">
                      <ThermometerSun className="w-4 h-4" />
                      Net Zero {results.targets.net_zero}
                    </div>
                  )}
                  {results.targets.certifications?.map((cert: string, index: number) => (
                    <div key={index} className="px-4 py-2 bg-blue-100 text-blue-800 rounded-full font-medium flex items-center gap-2">
                      <Award className="w-4 h-4" />
                      {cert}
                    </div>
                  ))}
                  {results.targets.reduction_targets?.map((target: number, index: number) => (
                    <div key={`red-${index}`} className="px-4 py-2 bg-purple-100 text-purple-800 rounded-full font-medium">
                      %{target} Azaltım Hedefi
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Scope Detection */}
            <div className="glass rounded-2xl p-6 shadow-xl">
              <h3 className="text-lg font-semibold text-forest-700 mb-4">Kapsam Tespiti</h3>
              <div className="grid grid-cols-3 gap-4">
                {(['scope1', 'scope2', 'scope3'] as const).map((scope, index) => {
                  const detected = results.scope_detection[scope]
                  const labels = ['Scope 1 (Doğrudan)', 'Scope 2 (Dolaylı)', 'Scope 3 (Değer Zinciri)']
                  return (
                    <div
                      key={scope}
                      className={`p-4 rounded-lg border-2 text-center ${
                        detected 
                          ? 'bg-green-50 border-green-300' 
                          : 'bg-red-50 border-red-300'
                      }`}
                    >
                      {detected ? (
                        <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-600" />
                      ) : (
                        <XCircle className="w-8 h-8 mx-auto mb-2 text-red-600" />
                      )}
                      <p className="font-medium text-sm">{labels[index]}</p>
                      <p className={`text-xs ${detected ? 'text-green-600' : 'text-red-600'}`}>
                        {detected ? 'Tespit edildi' : 'Bulunamadı'}
                      </p>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* ESG Classification */}
            <div className="glass rounded-2xl p-6 shadow-xl">
              <h3 className="text-lg font-semibold text-forest-700 mb-4">ESG Dağılımı</h3>
              <div className="space-y-4">
                {/* Environmental */}
                <div className="flex items-center gap-4">
                  <div className="w-32 flex items-center gap-2">
                    <Leaf className="w-5 h-5 text-green-600" />
                    <span className="text-sm font-medium">Çevresel</span>
                  </div>
                  <div className="flex-1 bg-sage-200 rounded-full h-4">
                    <div 
                      className="bg-gradient-to-r from-green-400 to-green-600 h-4 rounded-full transition-all duration-500"
                      style={{ width: getESGBarWidth(results.esg_classification.Environmental) }}
                    />
                  </div>
                  <span className="text-sm font-bold w-16 text-right text-green-700">
                    {Math.round(results.esg_classification.Environmental)}%
                  </span>
                </div>
                
                {/* Social */}
                <div className="flex items-center gap-4">
                  <div className="w-32 flex items-center gap-2">
                    <Users className="w-5 h-5 text-blue-600" />
                    <span className="text-sm font-medium">Sosyal</span>
                  </div>
                  <div className="flex-1 bg-sage-200 rounded-full h-4">
                    <div 
                      className="bg-gradient-to-r from-blue-400 to-blue-600 h-4 rounded-full transition-all duration-500"
                      style={{ width: getESGBarWidth(results.esg_classification.Social) }}
                    />
                  </div>
                  <span className="text-sm font-bold w-16 text-right text-blue-700">
                    {Math.round(results.esg_classification.Social)}%
                  </span>
                </div>
                
                {/* Governance */}
                <div className="flex items-center gap-4">
                  <div className="w-32 flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-purple-600" />
                    <span className="text-sm font-medium">Yönetişim</span>
                  </div>
                  <div className="flex-1 bg-sage-200 rounded-full h-4">
                    <div 
                      className="bg-gradient-to-r from-purple-400 to-purple-600 h-4 rounded-full transition-all duration-500"
                      style={{ width: getESGBarWidth(results.esg_classification.Governance) }}
                    />
                  </div>
                  <span className="text-sm font-bold w-16 text-right text-purple-700">
                    {Math.round(results.esg_classification.Governance)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Emission Values */}
            {results.emission_values.length > 0 && (
              <div className="glass rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-semibold text-forest-700 mb-4">
                  <TrendingUp className="w-5 h-5 inline mr-2" />
                  Tespit Edilen Emisyon Değerleri ({results.emission_values.length})
                </h3>
                <div className="space-y-3">
                  {results.emission_values.map((em, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-sage-50 rounded-lg">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 text-xs rounded font-medium ${
                          em.category?.includes('Scope 1') ? 'bg-red-100 text-red-700' :
                          em.category?.includes('Scope 2') ? 'bg-yellow-100 text-yellow-700' :
                          em.category?.includes('Scope 3') ? 'bg-blue-100 text-blue-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {em.category || 'Genel'}
                        </span>
                        <span className="text-sm text-sage-600 truncate max-w-xs">{em.context}</span>
                      </div>
                      <span className="font-bold text-forest-700 text-lg">
                        {em.value.toLocaleString()} {em.unit}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {results.recommendations.length > 0 && (
              <div className="glass rounded-2xl p-6 shadow-xl">
                <h3 className="text-lg font-semibold text-forest-700 mb-4">
                  <AlertTriangle className="w-5 h-5 inline mr-2 text-yellow-600" />
                  Öneriler ({results.recommendations.length})
                </h3>
                <ul className="space-y-3">
                  {results.recommendations.map((rec, index) => {
                    // Parse priority from the recommendation string
                    const isHigh = rec.includes('[HIGH]')
                    const isMedium = rec.includes('[MEDIUM]')
                    const priorityColor = isHigh ? 'border-l-red-500 bg-red-50' :
                                         isMedium ? 'border-l-yellow-500 bg-yellow-50' :
                                         'border-l-green-500 bg-green-50'
                    return (
                      <li key={index} className={`p-4 rounded-lg border-l-4 ${priorityColor}`}>
                        <span className="text-sage-700">{rec.replace('[HIGH] ', '').replace('[MEDIUM] ', '').replace('[LOW] ', '')}</span>
                      </li>
                    )
                  })}
                </ul>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
