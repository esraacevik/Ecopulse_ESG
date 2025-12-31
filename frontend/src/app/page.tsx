'use client'

import { motion, AnimatePresence } from 'framer-motion'
import EmissionForm from '@/components/EmissionForm'
import ResultsDisplay from '@/components/ResultsDisplay'
import FileUpload from '@/components/FileUpload'
import ActivitySearch from '@/components/ActivitySearch'
import AIChat from '@/components/AIChat'
import ReportGenerator from '@/components/ReportGenerator'
import ReportHistory from '@/components/ReportHistory'
import { useState } from 'react'
import { Calculator, Database, FileText, Bot, Upload, Info, BarChart3, FileSearch, Receipt, Brain } from 'lucide-react'
import ESGAnalyzer from '@/components/ESGAnalyzer'
import InvoiceScanner from '@/components/InvoiceScanner'
import MLDashboard from '@/components/MLDashboard'
import HintPanel, { QuickTip, StandardsBadge } from '@/components/HintPanel'
import { EmissionInput } from '@/services/api'

type TabType = 'home' | 'calculator' | 'database' | 'reports' | 'upload' | 'chat' | 'analyzer' | 'ocr' | 'ml'

interface SelectedActivity {
  id: string
  name: string
  category: string
  scope: string
  region: string
  source?: string
}

function ReportsTabContent({ results }: { results: any }) {
  const [subTab, setSubTab] = useState<'create' | 'history'>('create')

  return (
    <motion.div
      key="reports"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      {/* Sub-tabs */}
      <div className="flex gap-2 mb-6 border-b border-forest-200">
        <button
          onClick={() => setSubTab('create')}
          className={`px-4 py-2 font-medium transition ${
            subTab === 'create'
              ? 'text-forest-700 border-b-2 border-forest-600'
              : 'text-forest-500 hover:text-forest-700'
          }`}
        >
          Rapor Oluştur
        </button>
        <button
          onClick={() => setSubTab('history')}
          className={`px-4 py-2 font-medium transition ${
            subTab === 'history'
              ? 'text-forest-700 border-b-2 border-forest-600'
              : 'text-forest-500 hover:text-forest-700'
          }`}
        >
          Rapor Geçmişi
        </button>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {subTab === 'create' && (
          <motion.div
            key="create"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.2 }}
            className="grid lg:grid-cols-4 gap-6"
          >
            <div className="lg:col-span-1 space-y-4">
              <HintPanel
                title="ESG Rapor Oluşturma"
                hints={[
                  "Önce Hesaplama sekmesinden emisyon hesabı yapın",
                  "Şirket adı ve dönem bilgisi girin",
                  "PDF rapor otomatik olarak GRI 305 formatında oluşturulur",
                  "Rapor scope bazında dağılım grafiği içerir"
                ]}
                tips={[
                  "Akıllı Analiz sonuçları da rapora eklenebilir"
                ]}
              />
            </div>
            <div className="lg:col-span-3">
              <ReportGenerator results={results} />
            </div>
          </motion.div>
        )}

        {subTab === 'history' && (
          <motion.div
            key="history"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.2 }}
          >
            <ReportHistory />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function Home() {
  const [results, setResults] = useState(null)
  const [activeTab, setActiveTab] = useState<TabType>('home')
  const [selectedActivity, setSelectedActivity] = useState<SelectedActivity | null>(null)
  const [invoiceData, setInvoiceData] = useState<Partial<EmissionInput> | null>(null)

  const tabs = [
    { id: 'home' as TabType, label: 'Ana Sayfa', icon: BarChart3 },
    { id: 'calculator' as TabType, label: 'Hesaplama', icon: Calculator },
    { id: 'database' as TabType, label: 'Veritabanı', icon: Database },
    { id: 'analyzer' as TabType, label: 'ESG Analiz', icon: FileSearch },
    { id: 'ocr' as TabType, label: 'Fatura OCR', icon: Receipt },
    { id: 'ml' as TabType, label: 'Akıllı Analiz', icon: Brain },
    { id: 'reports' as TabType, label: 'Raporlar', icon: FileText },
    { id: 'upload' as TabType, label: 'Yükle', icon: Upload },
    { id: 'chat' as TabType, label: 'AI Asistan', icon: Bot },
  ]

  return (
    <main className="min-h-screen gradient-mesh relative overflow-hidden">
      {/* Organic background shapes */}
      <div className="organic-shape w-96 h-96 top-0 right-0 opacity-30" />
      <div className="organic-shape w-80 h-80 bottom-0 left-0 opacity-20" style={{ animationDelay: '2s' }} />
      
      <div className="relative z-10 container mx-auto px-4 py-12">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-6xl md:text-7xl font-display text-forest-700 mb-4">
            ECOLOGIA
          </h1>
          <p className="text-xl text-sage-600 font-body max-w-2xl mx-auto">
            AI-Powered Carbon Footprint Calculation & ESG Reporting
          </p>
          <div className="mt-8 h-1 w-24 bg-forest-500 mx-auto rounded-full" />
        </motion.header>

        {/* Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="max-w-5xl mx-auto mb-8"
        >
          <div className="glass rounded-2xl p-3 shadow-xl">
            {/* Desktop: 5 columns, Tablet: 3 columns, Mobile: 3 columns */}
            <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex flex-col items-center justify-center gap-1.5 px-2 py-3 rounded-xl font-medium transition-all ${
                      activeTab === tab.id
                        ? 'bg-forest-600 text-white shadow-lg'
                        : 'bg-white/60 text-sage-600 hover:bg-white hover:shadow-md'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-xs sm:text-sm truncate max-w-full">{tab.label}</span>
                  </button>
                )
              })}
            </div>
          </div>
        </motion.div>

        {/* Tab Content */}
        <div className="max-w-7xl mx-auto">
          <AnimatePresence mode="wait">
            {activeTab === 'home' && (
              <motion.div
                key="home"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-8"
              >
                {/* Stats Cards */}
                <div className="grid md:grid-cols-3 gap-6">
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 }}
                    className="glass rounded-2xl p-6 shadow-xl border-l-4 border-forest-500"
                  >
                    <div className="text-sm text-sage-600 mb-1">Emission Factors</div>
                    <div className="text-3xl font-display text-forest-700">277,000+</div>
                    <div className="text-xs text-sage-500 mt-1">Climatiq Database</div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                    className="glass rounded-2xl p-6 shadow-xl border-l-4 border-sage-500"
                  >
                    <div className="text-sm text-sage-600 mb-1">Desteklenen Ülke</div>
                    <div className="text-3xl font-display text-forest-700">200+</div>
                    <div className="text-xs text-sage-500 mt-1">Global Coverage</div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 }}
                    className="glass rounded-2xl p-6 shadow-xl border-l-4 border-blue-500"
                  >
                    <div className="text-sm text-sage-600 mb-1">Akıllı Araçlar</div>
                    <div className="text-3xl font-display text-forest-700">4</div>
                    <div className="text-xs text-sage-500 mt-1">Karşılaştırma, Hedef, Anomali, Tahmin</div>
                  </motion.div>
                </div>

                {/* Features */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="glass rounded-2xl p-8 shadow-xl"
                >
                  <h2 className="text-2xl font-display text-forest-700 mb-6">🚀 Bu Uygulama ile Neler Yapabilirsiniz?</h2>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-forest-100 rounded-lg">
                          <Calculator className="w-5 h-5 text-forest-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-sage-700">Emisyon Hesaplama</h3>
                          <p className="text-sm text-sage-600">Elektrik, yakıt, ulaşım ve diğer aktiviteler için CO2e hesaplayın</p>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-forest-100 rounded-lg">
                          <Database className="w-5 h-5 text-forest-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-sage-700">Emission Factor DB</h3>
                          <p className="text-sm text-sage-600">277,000+ faktörü arayın ve hesaplamalarınızda kullanın</p>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-forest-100 rounded-lg">
                          <FileText className="w-5 h-5 text-forest-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-sage-700">ESG Raporları</h3>
                          <p className="text-sm text-sage-600">GRI 305 uyumlu profesyonel PDF raporlar oluşturun</p>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-forest-100 rounded-lg">
                          <Upload className="w-5 h-5 text-forest-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-sage-700">Dosya Yükleme</h3>
                          <p className="text-sm text-sage-600">CSV/Excel dosyalarından emisyon verilerini otomatik çıkarın</p>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-forest-100 rounded-lg">
                          <Bot className="w-5 h-5 text-forest-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-sage-700">AI Asistan</h3>
                          <p className="text-sm text-sage-600">ESG konularında sorular sorun, öneriler alın</p>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-forest-100 rounded-lg">
                          <FileSearch className="w-5 h-5 text-forest-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-sage-700">ESG Analyzer</h3>
                          <p className="text-sm text-sage-600">PDF raporlarını ve metinleri analiz edin, risk skoru alın</p>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-forest-100 rounded-lg">
                          <Receipt className="w-5 h-5 text-forest-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-sage-700">Fatura OCR</h3>
                          <p className="text-sm text-sage-600">Elektrik/doğalgaz faturalarından otomatik veri çıkarın</p>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-forest-100 rounded-lg">
                          <Brain className="w-5 h-5 text-forest-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-sage-700">Akıllı Analiz</h3>
                          <p className="text-sm text-sage-600">Sektör karşılaştırma, net zero hedef ve tüketim tahmini</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 pt-6 border-t border-sage-200">
                    <button
                      onClick={() => setActiveTab('calculator')}
                      className="px-6 py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all"
                    >
                      Hesaplamaya Başla →
                    </button>
                  </div>
                </motion.div>

                {/* About Section */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="glass rounded-2xl p-8 shadow-xl"
                >
                  <h2 className="text-xl font-display text-forest-700 mb-4">ℹ️ Hakkında</h2>
                  <div className="grid md:grid-cols-2 gap-6 text-sm text-sage-600">
                    <div>
                      <h3 className="font-semibold text-sage-700 mb-2">Teknolojiler</h3>
                      <ul className="space-y-1">
                        <li>🌐 <strong>Frontend:</strong> Next.js + React</li>
                        <li>⚡ <strong>Backend:</strong> FastAPI</li>
                        <li>📊 <strong>API:</strong> Climatiq + Data.gov EPA</li>
                        <li>🤖 <strong>AI:</strong> Google Gemini</li>
                        <li>📄 <strong>PDF:</strong> ReportLab</li>
                      </ul>
                    </div>
                    <div>
                      <h3 className="font-semibold text-sage-700 mb-2">Standartlar</h3>
                      <ul className="space-y-1">
                        <li>📋 GHG Protocol</li>
                        <li>📋 GRI 305</li>
                        <li>📋 TCFD</li>
                        <li>📋 CDP</li>
                      </ul>
                    </div>
                  </div>
                  <p className="text-xs text-sage-400 mt-4">© 2025 ECOLOGIA - ESG Carbon Calculator</p>
                </motion.div>
              </motion.div>
            )}

            {activeTab === 'calculator' && (
              <motion.div
                key="calculator"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="grid lg:grid-cols-4 gap-6"
              >
                <div className="lg:col-span-1 space-y-4">
                  <HintPanel
                    title="Emisyon Hesaplama"
                    hints={[
                      "Scope 1: Doğrudan yakıt tüketimi (doğalgaz, benzin, dizel)",
                      "Scope 2: Satın alınan enerji (elektrik, ısıtma/soğutma)",
                      "Scope 3: Değer zinciri (ulaşım, su, atık, konaklama)"
                    ]}
                    tips={[
                      "Fatura OCR ile otomatik veri girişi yapabilirsiniz",
                      "Veritabanından faktör seçerek daha hassas hesaplama yapın"
                    ]}
                  />
                  <StandardsBadge standards={['GHG Protocol', 'GRI 305', 'ISO 14064']} />
                </div>
                <div className="lg:col-span-3 grid md:grid-cols-2 gap-6">
                <EmissionForm 
                  onCalculate={setResults} 
                  selectedActivity={selectedActivity} 
                  onActivityClear={() => setSelectedActivity(null)}
                  prefilledData={invoiceData}
                  onPrefilledDataUsed={() => setInvoiceData(null)}
                />
                <ResultsDisplay results={results} />
                </div>
              </motion.div>
            )}

            {activeTab === 'database' && (
              <motion.div
                key="database"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <ActivitySearch 
                  onActivitySelect={(activity) => {
                    setSelectedActivity(activity)
                    setActiveTab('calculator')
                  }}
                  selectedActivity={selectedActivity}
                />
              </motion.div>
            )}

            {activeTab === 'reports' && (
              <ReportsTabContent results={results} />
            )}

            {activeTab === 'upload' && (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="grid lg:grid-cols-4 gap-6"
              >
                <div className="lg:col-span-1 space-y-4">
                  <HintPanel
                    title="Toplu Veri Yükleme"
                    hints={[
                      "CSV veya Excel formatında dosya yükleyin",
                      "Kolon isimleri otomatik eşleştirilir",
                      "Birden fazla aktivite tek seferde hesaplanır",
                      "Sonuçlar Hesaplama sekmesine aktarılır"
                    ]}
                    tips={[
                      "Örnek kolonlar: elektrik_kwh, dogalgaz_m3, benzin_lt",
                      "Her satır bir dönem veya lokasyonu temsil edebilir"
                    ]}
                  />
                </div>
                <div className="lg:col-span-3">
                <FileUpload 
                  onCalculationComplete={(uploadResults) => {
                    setResults(uploadResults)
                  }}
                />
                </div>
              </motion.div>
            )}

            {activeTab === 'chat' && (
              <motion.div
                key="chat"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="grid lg:grid-cols-4 gap-6"
              >
                <div className="lg:col-span-1 space-y-4">
                  <HintPanel
                    title="AI Asistan"
                    hints={[
                      "ESG ve sürdürülebilirlik konularında sorular sorun",
                      "Emisyon azaltma stratejileri alın",
                      "Mevzuat ve raporlama standartları hakkında bilgi edinin",
                      "Sektörel en iyi uygulamaları öğrenin"
                    ]}
                    tips={[
                      "Örnek: 'Scope 3 emisyonları nasıl azaltılır?'",
                      "Örnek: 'GRI 305 raporlama gereksinimleri nelerdir?'"
                    ]}
                  />
                </div>
                <div className="lg:col-span-3">
                  <AIChat context={results} />
                </div>
              </motion.div>
            )}

            {activeTab === 'analyzer' && (
              <motion.div
                key="analyzer"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="grid lg:grid-cols-4 gap-6"
              >
                <div className="lg:col-span-1 space-y-4">
                  <HintPanel
                    title="ESG Doküman Analizi"
                    hints={[
                      "PDF veya metin yapıştırarak analiz yapın",
                      "Çevresel, Sosyal, Yönetişim dağılımı görün",
                      "Scope 1, 2, 3 tespiti otomatik yapılır",
                      "Risk skoru ve güven puanı hesaplanır"
                    ]}
                    tips={[
                      "En iyi sonuç için sürdürülebilirlik raporu yükleyin",
                      "Net Zero hedefleri otomatik tespit edilir"
                    ]}
                  />
                </div>
                <div className="lg:col-span-3">
                <ESGAnalyzer />
                </div>
              </motion.div>
            )}

            {activeTab === 'ocr' && (
              <motion.div
                key="ocr"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="grid lg:grid-cols-4 gap-6"
              >
                <div className="lg:col-span-1 space-y-4">
                  <HintPanel
                    title="Fatura Tarayıcı"
                    hints={[
                      "Elektrik veya doğalgaz faturası yükleyin",
                      "PDF veya görsel formatı desteklenir",
                      "Tüketim ve tutar otomatik çıkarılır",
                      "'Aktar' butonuyla Hesaplama'ya gönderin"
                    ]}
                    tips={[
                      "Net görüntü daha doğru sonuç verir",
                      "Türkçe ve İngilizce faturalar desteklenir"
                    ]}
                  />
                </div>
                <div className="lg:col-span-3">
                <InvoiceScanner 
                  onDataExtracted={(data) => {
                    setInvoiceData(data)
                    setActiveTab('calculator')
                  }}
                />
                </div>
              </motion.div>
            )}

            {activeTab === 'ml' && (
              <motion.div
                key="ml"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <MLDashboard />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </main>
  )
}
