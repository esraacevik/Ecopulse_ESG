'use client'

import React, { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  BarChart3, Target, AlertTriangle, TrendingUp, 
  Building2, Lightbulb, Loader2,
  CheckCircle, XCircle, ArrowRight, Upload, FileSpreadsheet,
  Zap, Activity, PieChart, Info, HelpCircle, FileText, X,
  ChevronDown, ChevronRight
} from 'lucide-react'
import { mlAPI, BenchmarkResponse, TargetResponse, AnomalyResponse, ForecastResponse } from '@/services/api'

type MLTab = 'overview' | 'benchmark' | 'target' | 'anomaly' | 'forecast'

// Hint/Notepad Component
function HintPanel({ title, hints, tips }: { title: string, hints: string[], tips?: string[] }) {
  return (
    <div className="bg-gradient-to-br from-sage-50 to-white rounded-xl p-4 border border-sage-200">
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 bg-forest-100 rounded-lg">
          <Lightbulb className="w-4 h-4 text-forest-600" />
        </div>
        <h4 className="font-semibold text-forest-700 text-sm">{title}</h4>
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

export default function MLDashboard() {
  const [activeTab, setActiveTab] = useState<MLTab>('overview')
  
  const tabs = [
    { id: 'overview' as MLTab, label: 'Genel Bakış', icon: BarChart3 },
    { id: 'benchmark' as MLTab, label: 'Sektör Karşılaştırma', icon: Building2 },
    { id: 'target' as MLTab, label: 'Net Zero Hedef', icon: Target },
    { id: 'anomaly' as MLTab, label: 'Anomali Tespiti', icon: AlertTriangle },
    { id: 'forecast' as MLTab, label: 'Tüketim Tahmini', icon: TrendingUp },
  ]
  
  return (
    <div className="space-y-6">
      {/* Sub Tabs - Grid Layout */}
      <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 p-2 bg-sage-100 rounded-xl">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex flex-col items-center justify-center gap-1 px-2 py-2.5 rounded-lg font-medium transition-all text-xs sm:text-sm ${
                activeTab === tab.id
                  ? 'bg-white text-forest-700 shadow'
                  : 'text-sage-600 hover:bg-sage-50'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="truncate">{tab.label}</span>
            </button>
          )
        })}
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'overview' && <OverviewSection key="overview" onTabChange={setActiveTab} />}
        {activeTab === 'benchmark' && <SectorBenchmark key="benchmark" />}
        {activeTab === 'target' && <TargetPathway key="target" />}
        {activeTab === 'anomaly' && <AnomalyDetection key="anomaly" />}
        {activeTab === 'forecast' && <EnergyForecast key="forecast" />}
      </AnimatePresence>
    </div>
  )
}

// ============================================================================
// Overview Section Component
// ============================================================================

function OverviewSection({ onTabChange }: { onTabChange: (tab: MLTab) => void }) {
  const features = [
    {
      id: 'benchmark' as MLTab,
      title: 'Sektör Karşılaştırma',
      description: 'Şirketinizi sektörünüzdeki diğer firmalarla karşılaştırın.',
      icon: Building2,
      color: 'blue',
      badge: 'A-F Rating'
    },
    {
      id: 'target' as MLTab,
      title: 'Net Zero Yol Haritası',
      description: 'Emisyon azaltım hedefleri ve yatırım planı oluşturun.',
      icon: Target,
      color: 'green',
      badge: 'SBTi Uyumlu'
    },
    {
      id: 'anomaly' as MLTab,
      title: 'Anomali Tespiti',
      description: 'Verilerinizdeki olağandışı değerleri tespit edin.',
      icon: AlertTriangle,
      color: 'amber',
      badge: 'Otomatik'
    },
    {
      id: 'forecast' as MLTab,
      title: 'Tüketim Tahmini',
      description: 'Gelecek dönem enerji tüketiminizi öngörün.',
      icon: TrendingUp,
      color: 'purple',
      badge: '%97 Doğruluk'
    }
  ]

  const colorClasses: Record<string, { bg: string, border: string, iconBg: string, text: string, subtext: string, badge: string }> = {
    blue: { bg: 'from-blue-50 to-blue-100', border: 'border-blue-200', iconBg: 'bg-blue-500', text: 'text-blue-900', subtext: 'text-blue-700', badge: 'bg-blue-100 text-blue-700' },
    green: { bg: 'from-green-50 to-green-100', border: 'border-green-200', iconBg: 'bg-green-500', text: 'text-green-900', subtext: 'text-green-700', badge: 'bg-green-100 text-green-700' },
    amber: { bg: 'from-amber-50 to-amber-100', border: 'border-amber-200', iconBg: 'bg-amber-500', text: 'text-amber-900', subtext: 'text-amber-700', badge: 'bg-amber-100 text-amber-700' },
    purple: { bg: 'from-purple-50 to-purple-100', border: 'border-purple-200', iconBg: 'bg-purple-500', text: 'text-purple-900', subtext: 'text-purple-700', badge: 'bg-purple-100 text-purple-700' },
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="grid lg:grid-cols-3 gap-6"
    >
      {/* Main Content */}
      <div className="lg:col-span-2 space-y-6">
        <div className="glass rounded-2xl p-6 shadow-xl">
          <h2 className="text-2xl font-display text-forest-700 mb-2">🎯 Karbon Performans Araçları</h2>
          <p className="text-sage-600 mb-6">
            Şirketinizin sürdürülebilirlik performansını değerlendirin, sektörünüzle kıyaslayın ve iyileştirme fırsatlarını keşfedin.
          </p>

          <div className="grid sm:grid-cols-2 gap-4">
            {features.map((feature) => {
              const Icon = feature.icon
              const colors = colorClasses[feature.color]
              return (
                <button
                  key={feature.id}
                  onClick={() => onTabChange(feature.id)}
                  className={`bg-gradient-to-br ${colors.bg} rounded-xl p-4 border ${colors.border} text-left hover:shadow-lg transition-all group`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-2 ${colors.iconBg} rounded-lg group-hover:scale-110 transition-transform`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className={`font-semibold ${colors.text}`}>{feature.title}</h3>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${colors.badge}`}>{feature.badge}</span>
                      </div>
                      <p className={`text-sm ${colors.subtext} mt-1`}>{feature.description}</p>
                    </div>
                  </div>
                  <div className="flex justify-end mt-2">
                    <ArrowRight className={`w-4 h-4 ${colors.subtext} opacity-0 group-hover:opacity-100 transition-opacity`} />
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="glass rounded-xl p-3 text-center">
            <div className="text-2xl font-display text-forest-700">1016</div>
            <div className="text-xs text-sage-600">Sektör Verisi</div>
          </div>
          <div className="glass rounded-xl p-3 text-center">
            <div className="text-2xl font-display text-forest-700">4</div>
            <div className="text-xs text-sage-600">Analiz Aracı</div>
          </div>
          <div className="glass rounded-xl p-3 text-center">
            <div className="text-2xl font-display text-forest-700">SBTi</div>
            <div className="text-xs text-sage-600">Standart Uyum</div>
          </div>
          <div className="glass rounded-xl p-3 text-center">
            <div className="text-2xl font-display text-forest-700">97%</div>
            <div className="text-xs text-sage-600">Doğruluk Oranı</div>
          </div>
        </div>
      </div>

      {/* Hint Panel */}
      <div className="space-y-4">
        <HintPanel
          title="Nasıl Kullanılır?"
          hints={[
            "Önce şirket verilerinizi Hesaplama sekmesinden girin",
            "Sektör Karşılaştırma ile konumunuzu görün",
            "Net Zero Hedef ile yol haritası oluşturun",
            "Tüketim Tahmini ile geleceği planlayın"
          ]}
          tips={[
            "NAICS kodu bilmiyorsanız sektör adı yazabilirsiniz"
          ]}
        />

        <div className="bg-gradient-to-br from-forest-50 to-forest-100 rounded-xl p-4 border border-forest-200">
          <div className="flex items-center gap-2 mb-3">
            <div className="p-1.5 bg-forest-500 rounded-lg">
              <CheckCircle className="w-4 h-4 text-white" />
            </div>
            <h4 className="font-semibold text-forest-700 text-sm">Desteklenen Standartlar</h4>
          </div>
          <div className="flex flex-wrap gap-2">
            <span className="text-xs px-2 py-1 bg-white rounded-full text-forest-700">GHG Protocol</span>
            <span className="text-xs px-2 py-1 bg-white rounded-full text-forest-700">SBTi</span>
            <span className="text-xs px-2 py-1 bg-white rounded-full text-forest-700">Paris 1.5°C</span>
            <span className="text-xs px-2 py-1 bg-white rounded-full text-forest-700">NAICS</span>
          </div>
        </div>

        {/* AI Insights Panel for Overview */}
        <div className="mt-4">
          <AIInsightsPanel 
            tabType="overview"
            compact={true}
            data={{
              total_emissions: 0, // Overview için genel öneriler
              emission_trend: 'stable',
              risk_score: 50,
              sbti_status: 'Not Set'
            }}
          />
        </div>
      </div>
    </motion.div>
  )
}

// ============================================================================
// Sector Benchmark Component
// ============================================================================

function SectorBenchmark() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<BenchmarkResponse | null>(null)
  const [formData, setFormData] = useState({
    company_name: '',
    naics_code: '',
    sector: '',
    total_emissions: '',
    revenue: '',
    employees: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await mlAPI.benchmark({
        company_name: formData.company_name,
        naics_code: formData.naics_code || undefined,
        sector: formData.sector || undefined,
        total_emissions: parseFloat(formData.total_emissions),
        revenue: parseFloat(formData.revenue),
        employees: formData.employees ? parseInt(formData.employees) : undefined
      })
      setResult(response)
    } catch (error) {
      console.error('Benchmark error:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRatingColor = (rating: string) => {
    const colors: Record<string, string> = {
      'A': 'bg-green-500',
      'B': 'bg-lime-500',
      'C': 'bg-yellow-500',
      'D': 'bg-orange-500',
      'F': 'bg-red-500'
    }
    return colors[rating] || 'bg-gray-500'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="grid lg:grid-cols-3 gap-6"
    >
      {/* Hint Panel */}
      <div className="lg:col-span-1 order-last lg:order-first">
        <HintPanel
          title="Sektör Karşılaştırma Nedir?"
          hints={[
            "Şirketinizi sektörünüzdeki diğer firmalarla kıyaslar",
            "Emisyon yoğunluğunuzu (kg CO2e/USD gelir) hesaplar",
            "A-F arası performans derecesi verir",
            "Sektör ortalamasına göre konumunuzu gösterir"
          ]}
          tips={[
            "NAICS kodu: 2-6 haneli endüstri sınıflandırma kodu",
            "Örnek: 336 = Ulaşım Ekipmanları Üretimi"
          ]}
        />
      </div>

      <div className="lg:col-span-2 grid md:grid-cols-2 gap-6">
      {/* Form */}
      <div className="glass rounded-2xl p-6 shadow-xl">
        <h3 className="text-xl font-display text-forest-700 mb-4">Şirket Bilgileri</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-sage-700 mb-1">Şirket Adı *</label>
            <input
              type="text"
              value={formData.company_name}
              onChange={(e) => setFormData({...formData, company_name: e.target.value})}
              className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500 focus:border-transparent"
              placeholder="Örn: ABC Holding A.Ş."
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-sm font-medium text-sage-700">NAICS Kodu</label>
                <NAICSCodeHelper />
              </div>
              <input
                type="text"
                value={formData.naics_code}
                onChange={(e) => setFormData({...formData, naics_code: e.target.value})}
                className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500 focus:border-transparent"
                placeholder="Örn: 336"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">veya Sektör</label>
              <input
                type="text"
                value={formData.sector}
                onChange={(e) => setFormData({...formData, sector: e.target.value})}
                className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500 focus:border-transparent"
                placeholder="Örn: Manufacturing"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-sage-700 mb-1">Toplam Emisyon (ton CO2e) *</label>
            <input
              type="number"
              value={formData.total_emissions}
              onChange={(e) => setFormData({...formData, total_emissions: e.target.value})}
              className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500 focus:border-transparent"
              placeholder="Örn: 50000"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-sage-700 mb-1">Yıllık Gelir (USD) *</label>
            <input
              type="number"
              value={formData.revenue}
              onChange={(e) => setFormData({...formData, revenue: e.target.value})}
              className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500 focus:border-transparent"
              placeholder="Örn: 500000000"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-sage-700 mb-1">Çalışan Sayısı</label>
            <input
              type="number"
              value={formData.employees}
              onChange={(e) => setFormData({...formData, employees: e.target.value})}
              className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500 focus:border-transparent"
              placeholder="Örn: 2000"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analiz Ediliyor...
              </>
            ) : (
              <>
                <BarChart3 className="w-5 h-5" />
                Karşılaştır
              </>
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      <div className="glass rounded-2xl p-6 shadow-xl">
        <h3 className="text-xl font-display text-forest-700 mb-4">Karşılaştırma Sonucu</h3>
        
        {!result ? (
          <div className="text-center text-sage-500 py-12">
            <Building2 className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Şirket bilgilerini girerek<br />sektör karşılaştırması yapın</p>
          </div>
        ) : result.success ? (
          <div className="space-y-6">
            <div className="text-center">
              <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full ${getRatingColor(result.metrics?.rating || 'C')} text-white text-5xl font-bold shadow-lg`}>
                {result.metrics?.rating}
              </div>
              <div className="mt-2 text-lg font-medium text-sage-700">{result.company}</div>
              <div className="text-sm text-sage-500">{result.sector}</div>
            </div>

            {result.metrics && (
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-sage-200">
                  <span className="text-sage-600">Şirket Yoğunluğu</span>
                  <span className="font-semibold text-sage-800">{result.metrics.company_intensity.toFixed(4)} kg/USD</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-sage-200">
                  <span className="text-sage-600">Sektör Ortalaması</span>
                  <span className="font-semibold text-sage-800">{result.metrics.sector_intensity.toFixed(4)} kg/USD</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-sage-200">
                  <span className="text-sage-600">Oran</span>
                  <span className={`font-semibold ${result.metrics.ratio < 1 ? 'text-green-600' : 'text-red-600'}`}>
                    {result.metrics.ratio.toFixed(2)}x
                  </span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-sage-600">Sektör İçi Sıralama</span>
                  <span className="font-semibold text-forest-600">En iyi %{100 - result.metrics.percentile}</span>
                </div>
              </div>
            )}

            {result.interpretation && (
              <div className="bg-sage-50 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <Lightbulb className="w-5 h-5 text-amber-500 mt-0.5" />
                  <p className="text-sm text-sage-700">{result.interpretation}</p>
                </div>
              </div>
            )}

            {/* AI Insights Panel - Results içinde */}
            {result.metrics && (
              <AIInsightsPanel 
                tabType="benchmark"
                compact={true}
                data={{
                  company_name: result.company || formData.company_name,
                  sector: result.sector || formData.sector,
                  company_metrics: {
                    intensity: result.metrics.company_intensity,
                    rating: result.metrics.rating,
                    ratio: result.metrics.ratio
                  },
                  sector_average: {
                    intensity: result.metrics.sector_intensity
                  },
                  percentile: result.metrics.percentile
                }}
              />
            )}
          </div>
        ) : (
          <div className="text-center text-red-500 py-12">
            <XCircle className="w-12 h-12 mx-auto mb-3" />
            <p>{result.error || 'Bir hata oluştu'}</p>
          </div>
        )}
      </div>
      </div>
    </motion.div>
  )
}

// ============================================================================
// Target Pathway Component
// ============================================================================

function TargetPathway() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<TargetResponse | null>(null)
  const [formData, setFormData] = useState({
    company_name: '',
    scope1_emissions: '',
    scope2_emissions: '',
    scope3_emissions: '',
    base_year: new Date().getFullYear().toString(),
    target_year: '2030',
    ambition: '1.5C' as '1.5C' | 'well_below_2C' | '2C'
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await mlAPI.generateTarget({
        company_name: formData.company_name,
        scope1_emissions: parseFloat(formData.scope1_emissions) || 0,
        scope2_emissions: parseFloat(formData.scope2_emissions) || 0,
        scope3_emissions: parseFloat(formData.scope3_emissions) || 0,
        base_year: parseInt(formData.base_year),
        target_year: parseInt(formData.target_year),
        ambition: formData.ambition
      })
      setResult(response)
    } catch (error) {
      console.error('Target error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="grid lg:grid-cols-4 gap-6">
        {/* Hint Panel */}
        <div className="lg:col-span-1">
          <HintPanel
            title="Net Zero Yol Haritası Nedir?"
            hints={[
              "Mevcut emisyonlarınızdan hedef yıla kadar azaltım planı oluşturur",
              "SBTi (Science Based Targets) standartlarına uyumlu hedefler belirler",
              "Yatırım gereksinimi ve tasarruf potansiyelini hesaplar",
              "Yıllık kilometre taşları ile ilerlemenizi takip edebilirsiniz"
            ]}
            tips={[
              "1.5°C hedefi en iddialı seçenektir (%4.2/yıl azaltım)"
            ]}
          />
        </div>
        
        <div className="glass rounded-2xl p-6 shadow-xl">
          <h3 className="text-xl font-display text-forest-700 mb-4">Emisyon Verileri</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">Şirket Adı</label>
              <input
                type="text"
                value={formData.company_name}
                onChange={(e) => setFormData({...formData, company_name: e.target.value})}
                className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500"
                placeholder="Şirket adı"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">Scope 1 (ton CO2e)</label>
              <input
                type="number"
                value={formData.scope1_emissions}
                onChange={(e) => setFormData({...formData, scope1_emissions: e.target.value})}
                className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500"
                placeholder="Doğrudan emisyonlar"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">Scope 2 (ton CO2e)</label>
              <input
                type="number"
                value={formData.scope2_emissions}
                onChange={(e) => setFormData({...formData, scope2_emissions: e.target.value})}
                className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500"
                placeholder="Enerji kaynaklı"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">Scope 3 (ton CO2e)</label>
              <input
                type="number"
                value={formData.scope3_emissions}
                onChange={(e) => setFormData({...formData, scope3_emissions: e.target.value})}
                className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500"
                placeholder="Değer zinciri"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-1">Baz Yıl</label>
                <input
                  type="number"
                  value={formData.base_year}
                  onChange={(e) => setFormData({...formData, base_year: e.target.value})}
                  className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-1">Hedef Yıl</label>
                <select
                  value={formData.target_year}
                  onChange={(e) => setFormData({...formData, target_year: e.target.value})}
                  className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500"
                >
                  <option value="2030">2030</option>
                  <option value="2035">2035</option>
                  <option value="2040">2040</option>
                  <option value="2050">2050</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">Hedef Seviyesi</label>
              <select
                value={formData.ambition}
                onChange={(e) => setFormData({...formData, ambition: e.target.value as any})}
                className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500"
              >
                <option value="1.5C">1.5°C Uyumlu (%4.2/yıl)</option>
                <option value="well_below_2C">2°C Altı (%2.5/yıl)</option>
                <option value="2C">2°C Uyumlu (%1.5/yıl)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Hesaplanıyor...
                </>
              ) : (
                <>
                  <Target className="w-5 h-5" />
                  Yol Haritası Oluştur
                </>
              )}
            </button>
          </form>
        </div>

        <div className="lg:col-span-2 space-y-6">
          {!result ? (
            <div className="glass rounded-2xl p-12 shadow-xl text-center text-sage-500">
              <Target className="w-16 h-16 mx-auto mb-4 opacity-30" />
              <p>Emisyon verilerinizi girerek<br />SBTi uyumlu yol haritası oluşturun</p>
            </div>
          ) : result.success ? (
            <>
              <div className="glass rounded-2xl p-6 shadow-xl">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-display text-forest-700">Özet</h3>
                  {result.summary?.sbti_aligned && (
                    <span className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                      <CheckCircle className="w-4 h-4" />
                      SBTi Uyumlu
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 bg-sage-50 rounded-lg">
                    <div className="text-2xl font-bold text-sage-800">
                      {result.summary?.current_emissions?.toLocaleString()}
                    </div>
                    <div className="text-xs text-sage-600">Mevcut (ton)</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-700">
                      {result.summary?.target_emissions?.toLocaleString()}
                    </div>
                    <div className="text-xs text-green-600">Hedef (ton)</div>
                  </div>
                  <div className="text-center p-3 bg-forest-50 rounded-lg">
                    <div className="text-2xl font-bold text-forest-700">
                      {result.summary?.total_reduction}
                    </div>
                    <div className="text-xs text-forest-600">Azaltım</div>
                  </div>
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-700">
                      {result.summary?.target_year}
                    </div>
                    <div className="text-xs text-blue-600">Hedef Yıl</div>
                  </div>
                </div>
              </div>

              {result.milestones && result.milestones.length > 0 && (
                <div className="glass rounded-2xl p-6 shadow-xl">
                  <h3 className="text-xl font-display text-forest-700 mb-4">Kilometre Taşları</h3>
                  <div className="flex items-center gap-2 overflow-x-auto pb-2">
                    {result.milestones.map((ms, i) => (
                      <div key={ms.year} className="flex items-center">
                        <div className="text-center min-w-[100px]">
                          <div className="text-lg font-bold text-forest-700">{ms.year}</div>
                          <div className="text-xs text-sage-600">{ms.target.toLocaleString()} ton</div>
                          <div className="text-xs text-green-600 font-medium">{ms.reduction}</div>
                        </div>
                        {i < result.milestones!.length - 1 && (
                          <ArrowRight className="w-5 h-5 text-sage-400 mx-2" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {result.investment && (
                <div className="glass rounded-2xl p-6 shadow-xl">
                  <h3 className="text-xl font-display text-forest-700 mb-4">Yatırım Tahmini</h3>
                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="bg-amber-50 rounded-lg p-4 text-center">
                      <div className="text-xl font-bold text-amber-700">{result.investment.total_investment}</div>
                      <div className="text-sm text-amber-600">Toplam Yatırım</div>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4 text-center">
                      <div className="text-xl font-bold text-green-700">{result.investment.estimated_annual_savings}</div>
                      <div className="text-sm text-green-600">Yıllık Tasarruf</div>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-4 text-center">
                      <div className="text-xl font-bold text-blue-700">{result.investment.payback_period}</div>
                      <div className="text-sm text-blue-600">Geri Ödeme</div>
                    </div>
                  </div>
                </div>
              )}

              {/* AI Önerileri */}
              <AIInsightsPanel 
                tabType="net_zero"
                data={{
                  company_name: formData.company_name,
                  scope1_emissions: parseFloat(formData.scope1_emissions) || 0,
                  scope2_emissions: parseFloat(formData.scope2_emissions) || 0,
                  scope3_emissions: parseFloat(formData.scope3_emissions) || 0,
                  target_year: parseInt(formData.target_year),
                  base_year: parseInt(formData.base_year),
                  reduction_target: parseFloat(result.summary?.total_reduction?.replace('%', '') || '0'),
                  milestones: result.milestones,
                  investment: result.investment
                }}
              />
            </>
          ) : (
            <div className="glass rounded-2xl p-12 shadow-xl text-center text-red-500">
              <XCircle className="w-16 h-16 mx-auto mb-4" />
              <p>{result.error || 'Bir hata oluştu'}</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

// ============================================================================
// NAICS Code Helper Component
// ============================================================================

function NAICSCodeHelper() {
  const [isOpen, setIsOpen] = useState(false)
  const [sectors, setSectors] = useState<Array<{naics: string, sector: string, factor: number}>>([])
  const [loading, setLoading] = useState(false)

  // Geçerli sektörleri backend'den al
  React.useEffect(() => {
    const fetchSectors = async () => {
      setLoading(true)
      try {
        const response = await mlAPI.getSectors()
        if (response.success && response.sectors) {
          setSectors(response.sectors)
        }
      } catch (error) {
        console.error('Sektörler yüklenemedi:', error)
        // Fallback: Geçerli kodlar (benchmarker'dan)
        setSectors([
          { naics: '111', sector: 'Agriculture', factor: 0.45 },
          { naics: '211', sector: 'Oil and Gas', factor: 1.85 },
          { naics: '221', sector: 'Utilities', factor: 1.20 },
          { naics: '236', sector: 'Construction', factor: 0.55 },
          { naics: '311', sector: 'Food Manufacturing', factor: 0.65 },
          { naics: '325', sector: 'Chemical Manufacturing', factor: 1.45 },
          { naics: '331', sector: 'Metal Manufacturing', factor: 1.75 },
          { naics: '336', sector: 'Transportation Equipment', factor: 0.85 },
          { naics: '423', sector: 'Wholesale Trade', factor: 0.25 },
          { naics: '441', sector: 'Retail Trade', factor: 0.20 },
          { naics: '481', sector: 'Air Transportation', factor: 2.50 },
          { naics: '484', sector: 'Truck Transportation', factor: 1.10 },
          { naics: '511', sector: 'Information Technology', factor: 0.15 },
          { naics: '522', sector: 'Financial Services', factor: 0.10 },
          { naics: '541', sector: 'Professional Services', factor: 0.12 },
          { naics: '611', sector: 'Education', factor: 0.18 },
          { naics: '621', sector: 'Healthcare', factor: 0.22 },
          { naics: '721', sector: 'Hospitality', factor: 0.35 }
        ])
      } finally {
        setLoading(false)
      }
    }
    fetchSectors()
  }, [])

  // Türkçe sektör isimleri
  const sectorNames: Record<string, string> = {
    'Agriculture': 'Tarım',
    'Oil and Gas': 'Petrol ve Gaz',
    'Utilities': 'Kamu Hizmetleri',
    'Construction': 'İnşaat',
    'Food Manufacturing': 'Gıda İmalatı',
    'Chemical Manufacturing': 'Kimyasal İmalat',
    'Metal Manufacturing': 'Metal İmalatı',
    'Transportation Equipment': 'Ulaşım Ekipmanları',
    'Wholesale Trade': 'Toptan Ticaret',
    'Retail Trade': 'Perakende Ticaret',
    'Air Transportation': 'Hava Taşımacılığı',
    'Truck Transportation': 'Kara Taşımacılığı',
    'Information Technology': 'Bilgi Teknolojileri',
    'Financial Services': 'Finansal Hizmetler',
    'Professional Services': 'Profesyonel Hizmetler',
    'Education': 'Eğitim',
    'Healthcare': 'Sağlık',
    'Hospitality': 'Konaklama'
  }

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="text-xs text-forest-600 hover:text-forest-700 underline flex items-center gap-1"
      >
        <Info className="w-3 h-3" />
        Kod Listesi
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 top-6 z-50 w-96 bg-white rounded-xl shadow-2xl border border-sage-200 max-h-96 overflow-hidden">
            <div className="sticky top-0 bg-forest-600 text-white p-3 flex items-center justify-between">
              <h4 className="font-semibold text-sm">NAICS Kodları (Geçerli)</h4>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white hover:text-sage-200 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="overflow-y-auto max-h-80 p-3">
              {loading ? (
                <div className="text-center py-8">
                  <Loader2 className="w-6 h-6 mx-auto mb-2 text-forest-600 animate-spin" />
                  <p className="text-xs text-sage-600">Yükleniyor...</p>
                </div>
              ) : sectors.length > 0 ? (
                <div className="space-y-2">
                  {sectors.map((item) => (
                    <div 
                      key={item.naics}
                      className="p-2 hover:bg-sage-50 rounded-lg transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-sm font-semibold text-forest-700">{item.naics}</span>
                        <span className="text-xs text-sage-600 text-right flex-1 ml-2">
                          {sectorNames[item.sector] || item.sector}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-sage-600 text-sm">
                  Sektör bulunamadı
                </div>
              )}
            </div>
            <div className="sticky bottom-0 bg-sage-50 p-2 border-t border-sage-200">
              <p className="text-xs text-sage-600 text-center">
                Kodu manuel olarak yazın
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

// ============================================================================
// AI Insights Panel Component
// ============================================================================

function AIInsightsPanel({ tabType, data, compact = false }: { tabType: string, data: Record<string, any>, compact?: boolean }) {
  const [loading, setLoading] = useState(false)
  const [insights, setInsights] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isExpanded, setIsExpanded] = useState(false)

  const fetchInsights = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await mlAPI.getAIInsights(tabType, data)
      if (response.success && response.insights) {
        setInsights(response.insights)
        setIsExpanded(true)
      } else {
        setError(response.error || 'AI önerileri alınamadı')
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'AI önerileri alınırken hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  // Kompakt mod: küçük, collapsible buton
  if (compact) {
    return (
      <div className="border-t border-sage-200 pt-4 mt-4">
        {!insights && !error && (
          <button
            onClick={fetchInsights}
            disabled={loading}
            className="w-full flex items-center justify-between p-3 bg-gradient-to-r from-forest-50 to-forest-100 hover:from-forest-100 hover:to-forest-200 rounded-lg transition-all border border-forest-200 group disabled:opacity-50"
          >
            <div className="flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-forest-600" />
              <span className="text-sm font-medium text-forest-700">
                {loading ? 'AI Önerileri Oluşturuluyor...' : 'AI Önerileri'}
              </span>
            </div>
            {loading ? (
              <Loader2 className="w-4 h-4 text-forest-600 animate-spin" />
            ) : (
              <ChevronRight className="w-4 h-4 text-forest-600 group-hover:translate-x-1 transition-transform" />
            )}
          </button>
        )}

        {loading && !insights && (
          <div className="p-3 bg-forest-50 border border-forest-200 rounded-lg">
            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 text-forest-600 animate-spin" />
              <span className="text-sm text-forest-700">AI önerileri oluşturuluyor...</span>
            </div>
          </div>
        )}

        {insights && (
          <div className="space-y-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-full flex items-center justify-between p-3 bg-gradient-to-r from-forest-50 to-forest-100 hover:from-forest-100 hover:to-forest-200 rounded-lg transition-all border border-forest-200"
            >
              <div className="flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-forest-600" />
                <span className="text-sm font-medium text-forest-700">AI Önerileri</span>
                <span className="text-xs px-2 py-0.5 bg-forest-200 text-forest-700 rounded-full">Hazır</span>
              </div>
              <ChevronDown className={`w-4 h-4 text-forest-600 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
            </button>
            
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="p-4 bg-sage-50 rounded-lg border border-sage-200 max-h-96 overflow-y-auto">
                  {error ? (
                    <div className="text-sm text-red-600">{error}</div>
                  ) : (
                    <p className="text-sm text-sage-700 whitespace-pre-wrap leading-relaxed">{insights}</p>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        )}

        {error && !insights && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            <div className="flex items-center gap-2">
              <XCircle className="w-4 h-4" />
              <span>{error}</span>
            </div>
            <button
              onClick={fetchInsights}
              className="mt-2 text-xs text-red-600 hover:text-red-700 underline"
            >
              Tekrar Dene
            </button>
          </div>
        )}
      </div>
    )
  }

  // Normal mod: tam panel
  if (!insights && !loading && !isExpanded) {
    return (
      <div className="glass rounded-xl p-4 shadow-lg border border-forest-200">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-forest-100 rounded-lg">
              <Lightbulb className="w-4 h-4 text-forest-600" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-forest-700">AI Önerileri</h4>
              <p className="text-xs text-sage-600">Qwen ile stratejik öneriler</p>
            </div>
          </div>
          <button
            onClick={fetchInsights}
            disabled={loading}
            className="px-3 py-1.5 bg-forest-600 hover:bg-forest-700 text-white text-xs font-medium rounded-lg transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin" />
                Yükleniyor...
              </>
            ) : (
              <>
                <Zap className="w-3 h-3" />
                Al
              </>
            )}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="glass rounded-xl p-4 shadow-lg border border-forest-200">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-forest-100 rounded-lg">
            <Lightbulb className="w-4 h-4 text-forest-600" />
          </div>
          <h4 className="text-sm font-semibold text-forest-700">AI Önerileri</h4>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1.5 text-sage-600 hover:text-forest-700 hover:bg-sage-100 rounded-lg transition-colors"
        >
          <ChevronDown className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
        </button>
      </div>

      {loading && (
        <div className="text-center py-4">
          <Loader2 className="w-5 h-5 mx-auto mb-2 text-forest-600 animate-spin" />
          <p className="text-xs text-sage-600">AI önerileri oluşturuluyor...</p>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs">
          {error}
        </div>
      )}

      {insights && isExpanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="overflow-hidden"
        >
          <div className="bg-sage-50 rounded-lg p-4 text-xs text-sage-800 whitespace-pre-wrap leading-relaxed max-h-96 overflow-y-auto border border-sage-200">
            {insights}
          </div>
        </motion.div>
      )}

      {insights && !isExpanded && (
        <div className="text-xs text-sage-600 italic line-clamp-2">
          {insights.substring(0, 100)}...
        </div>
      )}
    </div>
  )
}

// ============================================================================
// Anomaly Detection Component
// ============================================================================

function AnomalyDetection() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnomalyResponse | null>(null)
  const [fileName, setFileName] = useState('')
  const [previewData, setPreviewData] = useState<any[] | null>(null)
  const [fullData, setFullData] = useState<any[] | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setFileName(file.name)
    setResult(null)
    
    // Parse CSV
    const reader = new FileReader()
    reader.onload = (event) => {
      const text = event.target?.result as string
      const lines = text.split('\n').filter(line => line.trim())
      
      if (lines.length < 2) {
        setResult({ success: false, total_samples: 0, anomaly_count: 0, anomaly_ratio: 0, error: 'Dosya en az 2 satır içermeli (başlık + veri)' })
        return
      }
      
      const headers = lines[0].split(',').map(h => h.trim())
      
      // Tüm veriyi parse et
      const allData = lines.slice(1).map(line => {
        const values = line.split(',')
        const row: Record<string, any> = {}
        headers.forEach((h, i) => {
          row[h] = values[i]?.trim()
        })
        return row
      })
      
      // Önizleme için ilk 5 satır
      setPreviewData(allData.slice(0, 5))
      // Analiz için tüm veri
      setFullData(allData)
    }
    reader.onerror = () => {
      setResult({ success: false, total_samples: 0, anomaly_count: 0, anomaly_ratio: 0, error: 'Dosya okunurken hata oluştu' })
    }
    reader.readAsText(file)
  }

  const handleAnalyze = async () => {
    if (!fullData || fullData.length === 0) {
      setResult({ success: false, total_samples: 0, anomaly_count: 0, anomaly_ratio: 0, error: 'Lütfen önce bir dosya yükleyin' })
      return
    }
    
    if (fullData.length < 10) {
      setResult({ success: false, total_samples: fullData.length, anomaly_count: 0, anomaly_ratio: 0, error: 'En az 10 veri noktası gerekli' })
      return
    }
    
    setLoading(true)
    setResult(null)
    
    try {
      // Convert to numeric data (tüm veriyi kullan)
      const numericData = fullData.map(row => {
        const numRow: Record<string, number> = {}
        Object.entries(row).forEach(([key, value]) => {
          // Time kolonunu atla (string)
          if (key.toLowerCase() === 'time' || key.toLowerCase() === 'date') {
            return
          }
          const num = parseFloat(value as string)
          if (!isNaN(num)) {
            numRow[key] = num
          }
        })
        return numRow
      }).filter(row => Object.keys(row).length > 0) // Boş satırları filtrele

      if (numericData.length < 10) {
        setResult({ success: false, total_samples: numericData.length, anomaly_count: 0, anomaly_ratio: 0, error: 'En az 10 sayısal veri noktası gerekli' })
        return
      }

      const response = await mlAPI.detectAnomalies({
        data: numericData,
        contamination: 0.1
      })
      setResult(response)
    } catch (error: any) {
      console.error('Anomaly detection error:', error)
      setResult({ 
        success: false, 
        total_samples: 0, 
        anomaly_count: 0, 
        anomaly_ratio: 0, 
        error: error.response?.data?.error || error.message || 'Analiz sırasında hata oluştu' 
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="grid lg:grid-cols-3 gap-6"
    >
      {/* Hint Panel */}
      <div className="lg:col-span-1 order-last lg:order-first">
        <HintPanel
          title="Anomali Tespiti Nedir?"
          hints={[
            "Verilerinizdeki olağandışı değerleri otomatik tespit eder",
            "Beklenmedik artış veya düşüşleri bulur",
            "Veri kalitesi sorunlarını ortaya çıkarır",
            "Hatalı ölçüm veya kayıt hatalarını gösterir"
          ]}
          tips={[
            "CSV dosyanızda sayısal kolonlar olmalı",
            "Tarih, enerji tüketimi, üretim miktarı gibi veriler ideal"
          ]}
        />
      </div>
      
      <div className="lg:col-span-2 grid md:grid-cols-2 gap-6">
      {/* Upload Section */}
      <div className="glass rounded-2xl p-6 shadow-xl">
        <h3 className="text-xl font-display text-forest-700 mb-4">Veri Yükleme</h3>
        
        <div className="space-y-4">
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-sage-300 rounded-xl p-8 text-center cursor-pointer hover:border-forest-500 hover:bg-sage-50 transition-all"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.xlsx"
              onChange={handleFileChange}
              className="hidden"
            />
            <FileSpreadsheet className="w-12 h-12 mx-auto mb-3 text-sage-400" />
            <p className="text-sage-600 font-medium">CSV veya Excel dosyası yükleyin</p>
            <p className="text-sm text-sage-500 mt-1">Enerji tüketimi, emisyon verileri vb.</p>
          </div>

          {fileName && (
            <div className="flex items-center justify-between p-3 bg-sage-50 rounded-lg">
              <div className="flex items-center gap-2">
                <FileSpreadsheet className="w-5 h-5 text-forest-600" />
                <div>
                  <span className="text-sm font-medium text-forest-700">{fileName}</span>
                  {fullData && (
                    <p className="text-xs text-sage-600 mt-0.5">{fullData.length} satır yüklendi</p>
                  )}
                </div>
              </div>
              <CheckCircle className="w-4 h-4 text-green-500" />
            </div>
          )}

          {previewData && (
            <div className="space-y-2">
              <div className="text-sm font-medium text-sage-700">Önizleme (ilk 5 satır)</div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="bg-sage-100">
                      {Object.keys(previewData[0] || {}).map(key => (
                        <th key={key} className="px-2 py-1 text-left">{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {previewData.map((row, i) => (
                      <tr key={i} className="border-b border-sage-100">
                        {Object.values(row).map((val, j) => (
                          <td key={j} className="px-2 py-1">{String(val)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading || !fullData || fullData.length < 10}
            className="w-full py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analiz Ediliyor...
              </>
            ) : (
              <>
                <Activity className="w-5 h-5" />
                Anomali Tespit Et
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="glass rounded-2xl p-6 shadow-xl">
        <h3 className="text-xl font-display text-forest-700 mb-4">Tespit Sonuçları</h3>
        
        {!result ? (
          <div className="text-center text-sage-500 py-12">
            <AlertTriangle className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Anomali tespiti için<br />veri dosyası yükleyin</p>
          </div>
        ) : result.success ? (
          <div className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-sage-50 rounded-lg">
                <div className="text-2xl font-bold text-sage-800">{result.total_samples}</div>
                <div className="text-xs text-sage-600">Toplam Veri</div>
              </div>
              <div className="text-center p-4 bg-amber-50 rounded-lg">
                <div className="text-2xl font-bold text-amber-700">{result.anomaly_count}</div>
                <div className="text-xs text-amber-600">Anomali</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-700">{(result.anomaly_ratio * 100).toFixed(1)}%</div>
                <div className="text-xs text-red-600">Oran</div>
              </div>
            </div>

            {/* Anomaly Indicator */}
            <div className={`p-4 rounded-lg ${result.anomaly_count > 0 ? 'bg-amber-50 border border-amber-200' : 'bg-green-50 border border-green-200'}`}>
              <div className="flex items-center gap-2">
                {result.anomaly_count > 0 ? (
                  <>
                    <AlertTriangle className="w-5 h-5 text-amber-600" />
                    <span className="font-medium text-amber-800">
                      {result.anomaly_count} adet olağandışı değer tespit edildi
                    </span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="font-medium text-green-800">
                      Olağandışı değer tespit edilmedi
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* Anomaly Details */}
            {result.anomalies && result.anomalies.length > 0 && (
              <div className="space-y-4">
                <div className="text-sm font-medium text-sage-700">Anomali Detayları</div>
                
                {/* Anomaly List */}
                <div className="max-h-96 overflow-y-auto space-y-2">
                  {result.anomalies.map((idx) => {
                    const anomalyRow = fullData?.[idx]
                    if (!anomalyRow) return null
                    
                    // Time ve total_power değerlerini al
                    const time = anomalyRow.Time || anomalyRow.time || `Satır ${idx + 1}`
                    const totalPower = anomalyRow.total_power || anomalyRow.total_power_kW || 'N/A'
                    const powerValue = typeof totalPower === 'number' ? totalPower.toFixed(2) : totalPower
                    
                    // Anomali tipini belirle (yüksek/düşük)
                    const numericPower = parseFloat(powerValue)
                    const avgPower = fullData ? 
                      fullData.reduce((sum: number, row: any) => {
                        const p = parseFloat(row.total_power || row.total_power_kW || '0')
                        return sum + (isNaN(p) ? 0 : p)
                      }, 0) / fullData.length : 0
                    
                    const isHigh = !isNaN(numericPower) && numericPower > avgPower * 1.5
                    const isLow = !isNaN(numericPower) && numericPower < avgPower * 0.5
                    
                    return (
                      <div 
                        key={idx} 
                        className={`p-3 rounded-lg border ${
                          isHigh 
                            ? 'bg-red-50 border-red-200' 
                            : isLow 
                            ? 'bg-blue-50 border-blue-200' 
                            : 'bg-amber-50 border-amber-200'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-mono text-xs text-sage-600">#{idx + 1}</span>
                              {isHigh && (
                                <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-medium">
                                  Yüksek
                                </span>
                              )}
                              {isLow && (
                                <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                                  Düşük
                                </span>
                              )}
                            </div>
                            <div className="text-sm font-medium text-sage-800">
                              {String(time).substring(0, 19)}
                            </div>
                            <div className="text-xs text-sage-600 mt-1">
                              Güç: <span className="font-mono font-semibold">{powerValue} kW</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
                
                {/* Summary */}
                <div className="pt-2 border-t border-sage-200">
                  <div className="text-xs text-sage-600">
                    Toplam {result.anomalies.length} anomali tespit edildi
                  </div>
                </div>
              </div>
            )}

            {/* AI Insights Panel - Results içinde */}
            {result.anomalies && result.anomalies.length > 0 && (
              <AIInsightsPanel 
                tabType="anomaly"
                compact={true}
                data={{
                  anomaly_count: result.anomaly_count,
                  anomaly_indices: result.anomalies.map((a: any, idx: number) => idx),
                  data_summary: {
                    total_samples: result.total_samples,
                    anomaly_ratio: result.anomaly_ratio
                  },
                  anomaly_details: result.anomalies.map((a: any, idx: number) => ({
                    index: idx,
                    value: a.value,
                    is_high: a.value > (result.anomalies.reduce((sum: number, an: any) => sum + an.value, 0) / result.anomalies.length),
                    time: a.time || a.timestamp || `Row ${idx + 1}`
                  }))
                }}
              />
            )}
          </div>
        ) : (
          <div className="text-center text-red-500 py-12">
            <XCircle className="w-12 h-12 mx-auto mb-3" />
            <p>{result.error || 'Bir hata oluştu'}</p>
          </div>
        )}
      </div>
      </div>
    </motion.div>
  )
}

// ============================================================================
// Energy Forecast Component
// ============================================================================

function EnergyForecast() {
  const [formData, setFormData] = useState({
    location: 'Istanbul,TR',
    future_hours: '24',
    include_weather: true
  })
  const [historicalData, setHistoricalData] = useState<string>('')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [fileName, setFileName] = useState<string>('')
  const [dragActive, setDragActive] = useState(false)
  const [forecast, setForecast] = useState<ForecastResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Ensure formData always has defined values to prevent controlled/uncontrolled warning
  const safeFormData = {
    location: formData.location || 'Istanbul,TR',
    future_hours: formData.future_hours || '24',
    include_weather: formData.include_weather ?? true
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file: File) => {
    const validExtensions = ['csv']
    const fileExt = file.name.split('.').pop()?.toLowerCase()

    if (!validExtensions.includes(fileExt || '')) {
      setError('Geçersiz dosya tipi. Sadece CSV dosyası yükleyin.')
      return
    }

    setUploadedFile(file)
    setFileName(file.name)
    setError(null)
    setHistoricalData('')
    setForecast(null)

    // Read CSV file
    const reader = new FileReader()
    reader.onload = (event) => {
      const text = event.target?.result as string
      setHistoricalData(text)
    }
    reader.onerror = () => {
      setError('Dosya okunurken hata oluştu')
    }
    reader.readAsText(file)
  }

  const removeFile = () => {
    setUploadedFile(null)
    setFileName('')
    setHistoricalData('')
    setForecast(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const generateForecast = async () => {
    if (!historicalData.trim()) {
      setError('Lütfen geçmiş veri girin (CSV formatında)')
      return
    }

    try {
      setLoading(true)
      setError(null)

      // Parse CSV data
      const lines = historicalData.trim().split('\n')
      const headers = lines[0].split(',').map(h => h.trim())
      const data = lines.slice(1).map(line => {
        const values = line.split(',')
        const row: Record<string, any> = {}
        headers.forEach((h, i) => {
          const val = values[i]?.trim()
          const num = parseFloat(val)
          row[h] = isNaN(num) ? val : num
        })
        return row
      })

      if (data.length < 100) {
        setError('En az 100 veri noktası gerekli (model eğitimi için)')
        return
      }

      const response = await mlAPI.forecast({
        data: data,
        location: formData.location,
        future_hours: parseInt(formData.future_hours) || 24,
        include_weather: formData.include_weather
      })

      if (response.success && response.predictions) {
        setForecast(response)
      } else {
        setError(response.error || 'Tahmin oluşturulamadı')
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Tahmin oluşturulurken hata oluştu')
    } finally {
      setLoading(false)
    }
  }


  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="grid lg:grid-cols-3 gap-6"
    >
      {/* Hint Panel */}
      <div className="lg:col-span-1 order-last lg:order-first">
        <HintPanel
          title="Tüketim Tahmini Nedir?"
          hints={[
            "Mevcut tüketiminize dayalı gelecek tahmini yapar",
            "Büyüme oranı ve verimlilik iyileştirmesini hesaba katar",
            "Mevsimsel değişimleri modeller",
            "Tahmini CO2 emisyonunu hesaplar"
          ]}
          tips={[
            "Büyüme oranı: Şirketinizin yıllık büyüme tahmini",
            "Verimlilik: Enerji tasarruf hedefleriniz"
          ]}
        />
      </div>

      <div className="lg:col-span-2 grid md:grid-cols-2 gap-6">
      {/* Form */}
      <div className="glass rounded-2xl p-6 shadow-xl">
        <h3 className="text-xl font-display text-forest-700 mb-4">Tahmin Parametreleri</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-sage-700 mb-1">Konum</label>
            <input
              type="text"
              value={safeFormData.location}
              onChange={(e) => setFormData({...formData, location: e.target.value})}
              className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500"
              placeholder="Istanbul,TR"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-sage-700 mb-1">Tahmin Süresi (saat)</label>
            <select
              value={safeFormData.future_hours}
              onChange={(e) => setFormData({...formData, future_hours: e.target.value})}
              className="w-full px-4 py-2 rounded-lg border border-sage-300 focus:ring-2 focus:ring-forest-500"
            >
              <option value="24">24 saat (1 gün)</option>
              <option value="168">168 saat (1 hafta)</option>
              <option value="720">720 saat (1 ay)</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={safeFormData.include_weather}
              onChange={(e) => setFormData({...formData, include_weather: e.target.checked})}
              className="w-4 h-4 text-forest-600 rounded focus:ring-forest-500"
            />
            <label className="text-sm text-sage-700">Hava durumu özelliklerini dahil et</label>
          </div>

          <div>
            <label className="block text-sm font-medium text-sage-700 mb-1">Geçmiş Veri (CSV formatı)</label>
            
            {!uploadedFile ? (
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-all cursor-pointer ${
                  dragActive
                    ? 'border-forest-500 bg-forest-50'
                    : 'border-sage-300 hover:border-forest-400 bg-sage-50'
                }`}
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="w-8 h-8 mx-auto mb-2 text-sage-400" />
                <p className="text-sm font-medium text-sage-700 mb-1">
                  CSV dosyasını sürükleyip bırakın
                </p>
                <p className="text-xs text-sage-500 mb-2">
                  veya tıklayarak seçin
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  onChange={handleFileInput}
                  className="hidden"
                />
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-green-600" />
                    <div>
                      <p className="text-sm font-medium text-sage-700">{fileName}</p>
                      <p className="text-xs text-sage-500">
                        {historicalData.split('\n').length - 1} satır yüklendi
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={removeFile}
                    className="p-1 hover:bg-red-50 rounded transition-all"
                    type="button"
                  >
                    <X className="w-4 h-4 text-red-600" />
                  </button>
                </div>
                {historicalData && (
                  <div className="p-2 bg-sage-50 border border-sage-200 rounded text-xs text-sage-600 max-h-24 overflow-auto">
                    <p className="font-mono whitespace-pre-wrap">{historicalData.split('\n').slice(0, 3).join('\n')}</p>
                    {historicalData.split('\n').length > 3 && (
                      <p className="text-sage-400 mt-1">... ve {historicalData.split('\n').length - 3} satır daha</p>
                    )}
                  </div>
                )}
              </div>
            )}
            
            <p className="text-xs text-sage-500 mt-2">
              En az 100 satır veri gerekli. İlk satır başlıklar olmalı (Time, total_power, vb.)
            </p>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <button
            onClick={generateForecast}
            disabled={!historicalData?.trim() || loading}
            className="w-full py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Tahmin oluşturuluyor...
              </>
            ) : (
              <>
                <TrendingUp className="w-5 h-5" />
                Tahmin Oluştur
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="glass rounded-2xl p-6 shadow-xl">
        <h3 className="text-xl font-display text-forest-700 mb-4">Tüketim Tahmini</h3>
        
        {!forecast || !forecast.predictions ? (
          <div className="text-center text-sage-500 py-12">
            <TrendingUp className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Geçmiş veriyi girerek<br />AI modeli ile tahmin oluşturun</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Summary Stats */}
            {forecast.predictions && forecast.predictions.length > 0 && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-700">
                      {(forecast.predictions.reduce((sum, p) => sum + p.predicted_power, 0) / forecast.predictions.length).toFixed(1)}
                    </div>
                    <div className="text-xs text-purple-600">Ortalama (kW)</div>
                  </div>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-700">
                      {forecast.predictions.length}
                    </div>
                    <div className="text-xs text-blue-600">Tahmin Sayısı</div>
                  </div>
                </div>

                {/* Predictions Chart */}
                <div className="space-y-2">
                  <div className="text-sm font-medium text-sage-700">
                    Tahminler {forecast.weather_features && '(Hava durumu özellikleri dahil)'}
                  </div>
                  <div className="space-y-1 max-h-64 overflow-y-auto">
                    {forecast.predictions.map((p, i) => {
                      const maxValue = Math.max(...forecast.predictions!.map(x => x.predicted_power))
                      const width = (p.predicted_power / maxValue) * 100
                      const date = new Date(p.datetime)
                      const timeStr = date.toLocaleString('tr-TR', { 
                        month: 'short', 
                        day: 'numeric', 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })
                      return (
                        <div key={i} className="flex items-center gap-2">
                          <div className="w-32 text-xs text-sage-600">{timeStr}</div>
                          <div className="flex-1 h-6 bg-sage-100 rounded overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-purple-400 to-purple-600 rounded"
                              style={{ width: `${width}%` }}
                            />
                          </div>
                          <div className="w-20 text-xs text-right font-mono text-sage-700">
                            {p.predicted_power.toFixed(1)} kW
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* CO2 Estimation */}
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="w-5 h-5 text-green-600" />
                    <span className="font-medium text-green-800">Tahmini CO2 Emisyonu</span>
                  </div>
                  <div className="text-2xl font-bold text-green-700">
                    {(() => {
                      // predicted_power değerleri kW cinsinden (anlık güç)
                      // Her tahmin 1 saatlik, yani: 1 saat × kW = kWh
                      // Toplam kWh = tüm tahminlerin toplamı (her biri zaten 1 saatlik enerji tüketimini temsil ediyor)
                      const total_kwh = forecast.predictions.reduce((sum, p) => sum + p.predicted_power, 0)
                      // CO2 hesaplama: total_kwh × 0.4 kg CO2/kWh / 1000 = ton CO2e
                      const co2_ton = (total_kwh * 0.4) / 1000
                      // Küçük değerler için daha hassas gösterim
                      return co2_ton < 0.1 ? co2_ton.toFixed(2) : co2_ton.toFixed(1)
                    })()} ton CO2e
                  </div>
                  <div className="text-xs text-green-600 mt-1">
                    (Türkiye şebeke ortalaması: 0.4 kg CO2/kWh)
                  </div>
                  <div className="text-xs text-sage-500 mt-2 space-y-1">
                    <div>Toplam Enerji: {forecast.predictions.reduce((sum, p) => sum + p.predicted_power, 0).toFixed(1)} kWh</div>
                    <div>Ortalama Güç: {(forecast.predictions.reduce((sum, p) => sum + p.predicted_power, 0) / forecast.predictions.length).toFixed(2)} kW</div>
                  </div>
                </div>

                {/* AI Insights Panel - Results içinde */}
                <AIInsightsPanel 
                  tabType="forecast"
                  compact={true}
                  data={{
                    forecast_summary: {
                      total_predictions: forecast.predictions.length,
                      average_power: forecast.predictions.reduce((sum, p) => sum + p.predicted_power, 0) / forecast.predictions.length,
                      total_kwh: forecast.predictions.reduce((sum, p) => sum + p.predicted_power, 0),
                      estimated_co2_ton: (forecast.predictions.reduce((sum, p) => sum + p.predicted_power, 0) * 0.4) / 1000
                    },
                    current_consumption: forecast.predictions[0]?.predicted_power,
                    location: safeFormData.location,
                    weather_features: forecast.weather_features
                  }}
                />
              </>
            )}
          </div>
        )}
      </div>
      </div>
    </motion.div>
  )
}
