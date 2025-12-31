'use client'

import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Upload, FileText, X, CheckCircle, Table, AlertCircle, Calculator, Loader2 } from 'lucide-react'
import { uploadAPI, emissionAPI, EmissionInput } from '@/services/api'

interface FileUploadProps {
  onFileProcessed?: (data: any) => void
  onCalculationComplete?: (results: any) => void
}

interface ParsedData {
  rows: any[]
  columns: string[]
  row_count: number
  file_type: string
  filename: string
}

interface ExtractedEmissions {
  extracted_emissions: any[]
  matched_columns: string[]
  total_rows: number
}

export default function FileUpload({ onFileProcessed, onCalculationComplete }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [processing, setProcessing] = useState(false)
  const [calculating, setCalculating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [parsedData, setParsedData] = useState<ParsedData | null>(null)
  const [extractedEmissions, setExtractedEmissions] = useState<ExtractedEmissions | null>(null)
  const [calculationResults, setCalculationResults] = useState<any>(null)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = async (file: File) => {
    const validTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      'text/csv'
    ]
    const validExtensions = ['csv', 'xlsx', 'xls']
    const fileExt = file.name.split('.').pop()?.toLowerCase()

    if (!validTypes.includes(file.type) && !validExtensions.includes(fileExt || '')) {
      setError('Geçersiz dosya tipi. CSV veya Excel dosyası yükleyin.')
      return
    }

    setUploadedFile(file)
    setError(null)
    setProcessing(true)
    setParsedData(null)
    setExtractedEmissions(null)

    try {
      // First, try to extract emissions
      const extractResult = await uploadAPI.extractEmissions(file)
      
      if (extractResult.success) {
        setExtractedEmissions({
          extracted_emissions: extractResult.extracted_emissions,
          matched_columns: extractResult.matched_columns,
          total_rows: extractResult.total_rows
        })
        
        if (onFileProcessed && extractResult.extracted_emissions.length > 0) {
          onFileProcessed(extractResult.extracted_emissions)
        }
      }
      
      // Also parse the raw data
      const parseResult = await uploadAPI.parseFile(file)
      
      if (parseResult.success && parseResult.data) {
        setParsedData(parseResult.data)
      }
    } catch (err: any) {
      console.error('File processing error:', err)
      setError(err.response?.data?.detail || 'Dosya işlenirken hata oluştu')
    } finally {
      setProcessing(false)
    }
  }

  const removeFile = () => {
    setUploadedFile(null)
    setError(null)
    setParsedData(null)
    setExtractedEmissions(null)
    setCalculationResults(null)
  }

  // Calculate emissions from uploaded data
  const calculateFromUpload = async () => {
    if (!extractedEmissions || extractedEmissions.extracted_emissions.length === 0) {
      setError('Hesaplanacak veri bulunamadı')
      return
    }

    setCalculating(true)
    setError(null)

    try {
      // Sum up all values from extracted emissions
      const totals: EmissionInput = {
        category: 'Enerji',
        electricity_kwh: 0,
        natural_gas_m3: 0,
        diesel_litre: 0,
        petrol_litre: 0,
        lpg_litre: 0,
        coal_kg: 0,
        water_litre: 0,
        waste_kg: 0,
        vehicle_km: 0,
        vehicle_fuel_type: 'Dizel',
        flight_km: 0,
        flight_class: 'Ekonomi',
        region: 'TR',
        period: 'Monthly'
      }

      // Aggregate all rows
      for (const row of extractedEmissions.extracted_emissions) {
        if (row.electricity_kwh) totals.electricity_kwh += Number(row.electricity_kwh) || 0
        if (row.natural_gas_m3) totals.natural_gas_m3 += Number(row.natural_gas_m3) || 0
        if (row.diesel_litre) totals.diesel_litre += Number(row.diesel_litre) || 0
        if (row.petrol_litre) totals.petrol_litre += Number(row.petrol_litre) || 0
        if (row.lpg_litre) totals.lpg_litre += Number(row.lpg_litre) || 0
        if (row.coal_kg) totals.coal_kg += Number(row.coal_kg) || 0
        if (row.region) totals.region = row.region
      }

      console.log('Calculating with totals:', totals)
      
      // Call emission API
      const results = await emissionAPI.calculate(totals)
      console.log('Calculation results:', results)
      
      setCalculationResults(results)
      
      if (onCalculationComplete) {
        onCalculationComplete(results)
      }
    } catch (err: any) {
      console.error('Calculation error:', err)
      setError(err.response?.data?.detail || 'Hesaplama sırasında hata oluştu')
    } finally {
      setCalculating(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-8 shadow-xl"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-forest-100 rounded-lg">
          <Upload className="w-6 h-6 text-forest-600" />
        </div>
        <h2 className="text-2xl font-display text-forest-700">Upload Data File</h2>
      </div>

      {!uploadedFile ? (
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
          <FileText className="w-16 h-16 mx-auto mb-4 text-sage-400" />
          <p className="text-lg font-semibold text-sage-700 mb-2">
            Drag & drop your file here
          </p>
          <p className="text-sm text-sage-500 mb-4">
            or click to browse
          </p>
          <p className="text-xs text-sage-400 mb-4">
            Supported formats: PDF, Excel (.xlsx, .xls), CSV
          </p>
          <input
            type="file"
            id="file-upload"
            onChange={handleFileInput}
            accept=".pdf,.xlsx,.xls,.csv"
            className="hidden"
          />
          <label
            htmlFor="file-upload"
            className="inline-block px-6 py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg cursor-pointer transition-all"
          >
            Choose File
          </label>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <div>
                <p className="font-semibold text-sage-700">{uploadedFile.name}</p>
                <p className="text-xs text-sage-500">
                  {(uploadedFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>
            <button
              onClick={removeFile}
              className="p-2 hover:bg-red-50 rounded-lg transition-all"
            >
              <X className="w-5 h-5 text-red-600" />
            </button>
          </div>

          {processing && (
            <div className="text-center py-4">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-forest-600"></div>
              <p className="mt-2 text-sm text-sage-600">Processing file...</p>
            </div>
          )}

          {!processing && extractedEmissions && (
            <div className="space-y-4">
              {/* Matched Columns */}
              {extractedEmissions.matched_columns.length > 0 && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <p className="text-sm font-medium text-green-700">
                      {extractedEmissions.matched_columns.length} emisyon sütunu bulundu
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {extractedEmissions.matched_columns.map((col, i) => (
                      <span key={i} className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded">
                        {col}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Extracted Emissions Preview */}
              {extractedEmissions.extracted_emissions.length > 0 && (
                <div className="p-4 bg-forest-50 border border-forest-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <Table className="w-4 h-4 text-forest-600" />
                    <p className="text-sm font-medium text-forest-700">
                      {extractedEmissions.extracted_emissions.length} satır emisyon verisi çıkarıldı
                    </p>
                  </div>
                  <div className="max-h-48 overflow-auto">
                    <table className="w-full text-xs">
                      <thead className="bg-forest-100">
                        <tr>
                          {Object.keys(extractedEmissions.extracted_emissions[0] || {}).map((key) => (
                            <th key={key} className="px-2 py-1 text-left text-forest-700 font-medium">
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {extractedEmissions.extracted_emissions.slice(0, 5).map((row, i) => (
                          <tr key={i} className="border-b border-forest-100">
                            {Object.values(row).map((val, j) => (
                              <td key={j} className="px-2 py-1 text-sage-700">
                                {val as string}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {extractedEmissions.extracted_emissions.length > 5 && (
                    <p className="text-xs text-sage-500 mt-2">
                      +{extractedEmissions.extracted_emissions.length - 5} satır daha...
                    </p>
                  )}
                </div>
              )}

              {extractedEmissions.extracted_emissions.length === 0 && (
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-yellow-600" />
                    <p className="text-sm text-yellow-700">
                      Emisyon verisi bulunamadı. Sütun adlarının doğru olduğundan emin olun.
                    </p>
                  </div>
                </div>
              )}

              {/* Calculate Button */}
              {extractedEmissions.extracted_emissions.length > 0 && !calculationResults && (
                <button
                  onClick={calculateFromUpload}
                  disabled={calculating}
                  className="w-full py-4 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
                >
                  {calculating ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Hesaplanıyor...
                    </>
                  ) : (
                    <>
                      <Calculator className="w-5 h-5" />
                      Tüm Verileri Hesapla ({extractedEmissions.extracted_emissions.length} satır)
                    </>
                  )}
                </button>
              )}

              {/* Calculation Results */}
              {calculationResults && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-6 bg-gradient-to-br from-forest-50 to-sage-50 border-2 border-forest-300 rounded-xl"
                >
                  <div className="flex items-center gap-2 mb-4">
                    <CheckCircle className="w-5 h-5 text-forest-600" />
                    <h3 className="font-semibold text-forest-700">Hesaplama Sonucu</h3>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="p-4 bg-white rounded-lg border border-forest-100">
                      <p className="text-xs text-sage-500 mb-1">Toplam CO₂e</p>
                      <p className="text-2xl font-display text-forest-700">
                        {calculationResults.total_co2e_ton?.toFixed(2) || '0.00'} ton
                      </p>
                    </div>
                    <div className="p-4 bg-white rounded-lg border border-forest-100">
                      <p className="text-xs text-sage-500 mb-1">Detay</p>
                      <p className="text-2xl font-display text-forest-700">
                        {calculationResults.total_co2e_kg?.toFixed(0) || '0'} kg
                      </p>
                    </div>
                  </div>

                  {/* Scope Summary */}
                  {calculationResults.scope_summary && Object.keys(calculationResults.scope_summary).length > 0 && (
                    <div className="space-y-2 mb-4">
                      <p className="text-xs font-medium text-sage-600">Scope Dağılımı:</p>
                      {Object.entries(calculationResults.scope_summary).map(([scope, value]) => (
                        <div key={scope} className="flex justify-between text-sm p-2 bg-white rounded border border-sage-100">
                          <span className="text-sage-700">{scope}</span>
                          <span className="font-medium text-forest-600">{(value as number).toFixed(2)} ton</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Activity Details */}
                  {calculationResults.results && calculationResults.results.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs font-medium text-sage-600">Detaylı Sonuçlar:</p>
                      {calculationResults.results.map((result: any, i: number) => (
                        <div key={i} className="p-3 bg-white rounded border border-sage-100">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="text-sm font-medium text-sage-700">{result.activity_name}</p>
                              <p className="text-xs text-sage-500">{result.amount} {result.unit}</p>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-semibold text-forest-600">{result.co2e_kg?.toFixed(2)} kg</p>
                              <p className="text-xs text-sage-500">{result.source}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <button
                    onClick={() => setCalculationResults(null)}
                    className="mt-4 w-full py-2 bg-sage-100 hover:bg-sage-200 text-sage-700 font-medium rounded-lg transition-all text-sm"
                  >
                    Yeni Hesaplama Yap
                  </button>
                </motion.div>
              )}
            </div>
          )}

          {!processing && !extractedEmissions && parsedData && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-700">
                ✅ {parsedData.row_count} satır yüklendi. Emisyon sütunları otomatik algılanamadı.
              </p>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Supported Formats Info */}
      <div className="mt-6 p-4 bg-sage-50 rounded-lg border border-sage-200">
        <p className="text-sm font-medium text-sage-700 mb-2">📋 Desteklenen Sütun Adları:</p>
        <div className="flex flex-wrap gap-2 text-xs">
          {['electricity_kwh', 'natural_gas_m3', 'diesel_litre', 'petrol_litre', 'lpg_litre', 'coal_kg', 'region', 'period'].map((col) => (
            <span key={col} className="px-2 py-1 bg-white text-sage-600 rounded border border-sage-200">
              {col}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  )
}

