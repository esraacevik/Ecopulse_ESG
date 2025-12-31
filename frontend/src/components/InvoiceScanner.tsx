'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Receipt, 
  Upload, 
  Zap, 
  FileText,
  CheckCircle,
  XCircle,
  ArrowRight,
  Lightbulb
} from 'lucide-react'
import { analyzerAPI, InvoiceDataResponse, EmissionInput } from '@/services/api'

interface InvoiceScannerProps {
  onDataExtracted?: (data: Partial<EmissionInput>) => void
}

export default function InvoiceScanner({ onDataExtracted }: InvoiceScannerProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<InvoiceDataResponse | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const handleFileSelect = (file: File) => {
    const validExtensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    const ext = '.' + file.name.toLowerCase().split('.').pop()
    
    if (!validExtensions.includes(ext)) {
      setError(`Desteklenmeyen format. Kabul edilenler: ${validExtensions.join(', ')}`)
      return
    }
    
    setSelectedFile(file)
    setError(null)
    setResults(null)
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
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0])
    }
  }

  const handleScan = async () => {
    if (!selectedFile) {
      setError('Lütfen bir dosya seçin')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const response = await analyzerAPI.extractInvoice(selectedFile)
      setResults(response)
      // Don't auto-transfer, wait for user to click the button
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Fatura tarama sırasında hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  const handleUseData = () => {
    if (results && onDataExtracted) {
      onDataExtracted({
        electricity_kwh: results.electricity_kwh,
        natural_gas_m3: results.natural_gas_m3,
        water_litre: results.water_litre,
      })
    }
  }

  const clearFile = () => {
    setSelectedFile(null)
    setResults(null)
    setError(null)
  }

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
            <Receipt className="w-6 h-6 text-forest-600" />
          </div>
          <div>
            <h2 className="text-2xl font-display text-forest-700">Fatura Tarayıcı (OCR)</h2>
            <p className="text-sm text-sage-600">
              Elektrik, doğalgaz veya su faturanızı tarayın, verileri otomatik çıkaralım
            </p>
          </div>
        </div>

        {/* Info Box */}
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start gap-2">
            <Lightbulb className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Nasıl Çalışır?</p>
              <ul className="list-disc list-inside space-y-1 text-blue-700">
                <li>Fatura görüntüsünü veya PDF'ini yükleyin</li>
                <li>OCR teknolojisi ile tüketim verileri otomatik tespit edilir</li>
                <li>Çıkarılan veriler hesaplayıcıya aktarılabilir</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Upload Area */}
        {!selectedFile ? (
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${
              dragActive
                ? 'border-forest-500 bg-forest-50'
                : 'border-sage-300 hover:border-forest-400'
            }`}
          >
            <Receipt className="w-16 h-16 mx-auto mb-4 text-sage-400" />
            <p className="text-lg font-semibold text-sage-700 mb-2">
              Fatura dosyasını buraya sürükleyin
            </p>
            <p className="text-sm text-sage-500 mb-4">
              veya tıklayarak seçin
            </p>
            <p className="text-xs text-sage-400 mb-4">
              Desteklenen formatlar: PDF, PNG, JPG, JPEG, TIFF, BMP
            </p>
            <input
              type="file"
              id="invoice-upload"
              onChange={handleInputChange}
              accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp"
              className="hidden"
            />
            <label
              htmlFor="invoice-upload"
              className="inline-block px-6 py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg cursor-pointer transition-all"
            >
              Dosya Seç
            </label>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Selected File */}
            <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-3">
                <FileText className="w-8 h-8 text-green-600" />
                <div>
                  <p className="font-semibold text-sage-700">{selectedFile.name}</p>
                  <p className="text-xs text-sage-500">
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
              <button
                onClick={clearFile}
                className="p-2 hover:bg-red-50 rounded-lg transition-all"
              >
                <XCircle className="w-5 h-5 text-red-600" />
              </button>
            </div>

            {/* Scan Button */}
            <button
              onClick={handleScan}
              disabled={loading}
              className="w-full py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
                  OCR Taraması Yapılıyor...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Faturayı Tara
                </>
              )}
            </button>
          </div>
        )}

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
            className="glass rounded-2xl p-6 shadow-xl"
          >
            <div className="flex items-center gap-2 mb-4">
              {results.success ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : (
                <XCircle className="w-6 h-6 text-red-600" />
              )}
              <h3 className="text-lg font-semibold text-forest-700">
                {results.success ? 'Fatura Verileri Çıkarıldı' : 'Veri Çıkarılamadı'}
              </h3>
            </div>

            {results.error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {results.error}
              </div>
            )}

            {results.success && (
              <>
                {/* Extracted Data */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  {/* Electricity */}
                  <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-sage-600 mb-1">Elektrik Tüketimi</p>
                    <p className="text-2xl font-bold text-yellow-700">
                      {results.electricity_kwh > 0 
                        ? `${results.electricity_kwh.toLocaleString()} kWh`
                        : 'Tespit edilemedi'}
                    </p>
                  </div>

                  {/* Natural Gas */}
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-sage-600 mb-1">Doğalgaz Tüketimi</p>
                    <p className="text-2xl font-bold text-blue-700">
                      {results.natural_gas_m3 > 0 
                        ? `${results.natural_gas_m3.toLocaleString()} m³`
                        : 'Tespit edilemedi'}
                    </p>
                  </div>

                  {/* Water */}
                  <div className="p-4 bg-cyan-50 border border-cyan-200 rounded-lg">
                    <p className="text-sm text-sage-600 mb-1">Su Tüketimi</p>
                    <p className="text-2xl font-bold text-cyan-700">
                      {results.water_litre > 0 
                        ? `${results.water_litre.toLocaleString()} L`
                        : 'Tespit edilemedi'}
                    </p>
                  </div>

                  {/* Amount */}
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-sage-600 mb-1">Fatura Tutarı</p>
                    <p className="text-2xl font-bold text-green-700">
                      {results.amount_tl > 0 
                        ? `${results.amount_tl.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺`
                        : 'Tespit edilemedi'}
                    </p>
                    {results.period && (
                      <p className="text-sm text-sage-500 mt-1">
                        Dönem: {results.period}
                      </p>
                    )}
                  </div>
                </div>

                {/* Use Data Button */}
                {onDataExtracted && (results.electricity_kwh > 0 || results.natural_gas_m3 > 0 || results.water_litre > 0) && (
                  <button
                    onClick={handleUseData}
                    className="w-full py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-all duration-300 flex items-center justify-center gap-2"
                  >
                    <ArrowRight className="w-5 h-5" />
                    Bu Verileri Hesaplayıcıya Aktar
                  </button>
                )}
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

