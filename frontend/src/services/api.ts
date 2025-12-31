import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 saniye timeout
})

export interface EmissionInput {
  category: string
  // Scope 1 - Direct
  natural_gas_m3: number
  diesel_litre: number
  petrol_litre: number
  lpg_litre: number
  coal_kg: number
  fuel_oil_litre: number     // NEW: Fuel oil
  biogas_kwh: number         // NEW: Biogas
  refrigerant_kg: number     // NEW: Refrigerant leakage (R-134a etc)
  vehicle_km: number
  vehicle_fuel_type: string
  // Scope 2 - Indirect Energy
  electricity_kwh: number
  heating_kwh: number
  cooling_kwh: number
  // Scope 3 - Value Chain
  water_litre: number
  waste_kg: number
  waste_type: string         // NEW: landfill, recycling, incineration
  flight_km: number
  flight_class: string
  hotel_nights: number       // NEW: Hotel stays
  taxi_km: number            // NEW: Taxi travel
  train_km: number           // NEW: Train travel
  bus_km: number             // NEW: Bus travel
  metro_km: number           // NEW: Metro/subway travel
  freight_ton_km: number     // NEW: Freight transport
  paper_kg: number           // NEW: Purchased paper
  // Settings
  region: string
  period: string
}

export interface EmissionResult {
  activity_name: string
  amount: number
  unit: string
  co2e_kg: number
  co2e_ton: number
  scope: string
  category: string
  region: string
  source: string
  confidence?: string
}

export interface EmissionCalculationResponse {
  results: EmissionResult[]
  total_co2e_kg: number
  total_co2e_ton: number
  scope_summary: Record<string, number>
  timestamp: string
}

export const emissionAPI = {
  calculate: async (input: EmissionInput): Promise<EmissionCalculationResponse> => {
    const response = await api.post<EmissionCalculationResponse>('/api/v1/emission/calculate', input)
    return response.data
  },
  
  getSources: async () => {
    const response = await api.get('/api/v1/emission/sources')
    return response.data
  },
}

export interface ReportProgressMessage {
  type: 'progress' | 'complete' | 'error'
  message?: string
  step?: string
  percentage?: number
  filename?: string
  file_path?: string
}

export interface ReportGenerateRequest {
  results: EmissionResult[]
  company_name: string
  period: string
  filename?: string
}

export const reportAPI = {
  generate: async (data: any) => {
    const response = await api.post('/api/v1/report/generate', data)
    return response.data
  },
  
  list: async () => {
    const response = await api.get('/api/v1/report/list')
    return response.data
  },
  
  delete: async (filename: string) => {
    const response = await api.delete(`/api/v1/report/delete/${encodeURIComponent(filename)}`)
    return response.data
  },
  
  generateStream: async (
    data: ReportGenerateRequest,
    onProgress: (message: ReportProgressMessage) => void
  ): Promise<string> => {
    return new Promise((resolve, reject) => {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // Use fetch with POST for SSE (with timeout)
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 300000) // 5 dakika timeout
      
      fetch(`${API_URL}/api/v1/report/generate-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        signal: controller.signal,
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          
          const reader = response.body?.getReader()
          const decoder = new TextDecoder()
          
          if (!reader) {
            throw new Error('No response body')
          }
          
          let buffer = ''
          
          const readStream = () => {
            reader.read().then(({ done, value }) => {
              if (done) {
                // Check if we have any remaining data in buffer
                if (buffer.trim()) {
                  processBuffer(buffer)
                }
                return
              }
              
              buffer += decoder.decode(value, { stream: true })
              const lines = buffer.split('\n')
              
              // Keep last incomplete line in buffer
              buffer = lines.pop() || ''
              
              // Process complete lines
              for (const line of lines) {
                if (line.trim()) {
                  processLine(line)
                }
              }
              
              readStream()
            }).catch(err => {
              reject(err)
            })
          }
          
          const processLine = (line: string) => {
            if (line.startsWith('data: ')) {
              try {
                const jsonData = line.slice(6).trim()
                if (!jsonData) return
                
                const data = JSON.parse(jsonData)
                const message: ReportProgressMessage = data
                
                onProgress(message)
                
                if (message.type === 'complete') {
                  if (message.filename) {
                    resolve(message.filename)
                  } else {
                    reject(new Error('Report completed but no filename provided'))
                  }
                } else if (message.type === 'error') {
                  reject(new Error(message.message || 'Unknown error'))
                }
              } catch (e) {
                console.error('Error parsing SSE message:', e, line)
              }
            }
          }
          
          const processBuffer = (buf: string) => {
            if (buf.trim()) {
              processLine(buf)
            }
          }
          
          readStream()
        })
        .catch(err => {
          clearTimeout(timeoutId)
          if (err.name === 'AbortError') {
            reject(new Error('Rapor oluşturma zaman aşımına uğradı (5 dakika)'))
          } else {
            reject(err)
          }
        })
    })
  },
}

export const aiAPI = {
  chat: async (message: string, context?: any) => {
    const response = await api.post('/api/v1/ai/chat', { message, context })
    return response.data
  },
}

export const activityAPI = {
  search: async (query: string, scope?: string, category?: string, region?: string, limit: number = 50) => {
    const params: any = { query, limit }
    if (scope) params.scope = scope
    if (category) params.category = category
    if (region) params.region = region
    const response = await api.get('/api/v1/activity/search', { params })
    return response.data
  },
  
  getPopular: async (limit: number = 20) => {
    const response = await api.get('/api/v1/activity/popular', { params: { limit } })
    return response.data
  },
  
  getCategories: async () => {
    const response = await api.get('/api/v1/activity/categories')
    return response.data
  },
}

export const uploadAPI = {
  parseFile: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/v1/upload/parse', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },
  
  extractEmissions: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/v1/upload/extract-emissions', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },
}

// ESG Analysis Response Interface - Enhanced v2
export interface ESGAnalysisResponse {
  success: boolean
  scope_detection: {
    scope1: boolean
    scope2: boolean
    scope3: boolean
  }
  emission_values: Array<{
    value: number
    unit: string
    context: string
    category?: string
    raw_value?: string
  }>
  esg_classification: {
    Environmental: number  // Now percentage 0-100
    Social: number
    Governance: number
  }
  risk_score: number
  summary: string
  recommendations: string[]
  // New v2 fields
  sentiment?: {
    score: number
    label: string
    positive_indicators: number
    negative_indicators: number
    high_risk_count: number
    medium_risk_count: number
  }
  targets?: {
    net_zero?: number
    reduction_targets?: number[]
    certifications?: string[]
  }
  confidence?: {
    score: number
    level: string
  }
  risk_details?: {
    total: number
    level: string
    color: string
    components: {
      scope_coverage: number
      emission_data: number
      esg_balance: number
      sentiment: number
      transparency: number
    }
  }
  error?: string
}

// OCR Response Interface
export interface OCRResponse {
  success: boolean
  raw_text: string
  extracted_data: Array<{
    category: string
    scope: string
    amount: number
    unit: string
    source: string
    confidence: number
  }>
  confidence: number
  error?: string
}

// Invoice Data Response Interface
export interface InvoiceDataResponse {
  success: boolean
  electricity_kwh: number
  natural_gas_m3: number
  water_litre: number
  period: string
  amount_tl: number
  raw_values: Array<{
    type: string
    value: number
    unit: string
  }>
  error?: string
}

export const analyzerAPI = {
  // Text Analysis
  analyzeText: async (text: string): Promise<ESGAnalysisResponse> => {
    const response = await api.post('/api/v1/analyzer/text', { text })
    return response.data
  },
  
  // PDF Analysis
  analyzePDF: async (file: File): Promise<ESGAnalysisResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/v1/analyzer/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },
  
  // OCR Image
  ocrImage: async (file: File): Promise<OCRResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/v1/analyzer/ocr/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },
  
  // OCR PDF
  ocrPDF: async (file: File): Promise<OCRResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/v1/analyzer/ocr/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },
  
  // Invoice Extraction
  extractInvoice: async (file: File): Promise<InvoiceDataResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/v1/analyzer/invoice', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },
  
  // Analyzer Status
  getStatus: async () => {
    const response = await api.get('/api/v1/analyzer/status')
    return response.data
  },
}

// ============================================================================
// ML API - Machine Learning Endpoints
// ============================================================================

export interface BenchmarkRequest {
  company_name: string
  naics_code?: string
  sector?: string
  total_emissions: number
  revenue: number
  employees?: number
}

export interface BenchmarkResponse {
  success: boolean
  company: string
  sector?: string
  metrics?: {
    company_intensity: number
    sector_intensity: number
    ratio: number
    percentile: number
    rating: string
  }
  interpretation?: string
  error?: string
}

export interface TargetRequest {
  company_name: string
  scope1_emissions: number
  scope2_emissions: number
  scope3_emissions: number
  base_year: number
  target_year: number
  ambition: '1.5C' | 'well_below_2C' | '2C'
}

export interface TargetResponse {
  success: boolean
  summary?: {
    company: string
    current_emissions: number
    target_year: number
    target_emissions: number
    total_reduction: string
    sbti_aligned: boolean
  }
  milestones?: Array<{
    year: number
    target: number
    reduction: string
  }>
  scope_strategies?: Record<string, {
    current_emissions: number
    recommended_actions: Array<{
      action: string
      description: string
      reduction_potential: string
      reduction_tons: number
      cost_level: string
      timeline: string
    }>
  }>
  investment?: {
    total_investment: string
    estimated_annual_savings: string
    payback_period: string
    investment_breakdown: Array<{
      action: string
      scope: string
      estimated_cost: string
      cost_level: string
    }>
  }
  error?: string
}

export interface AnomalyRequest {
  data: Array<Record<string, number>>
  columns?: string[]
  contamination?: number
}

export interface AnomalyResponse {
  success: boolean
  total_samples: number
  anomaly_count: number
  anomaly_ratio: number
  anomalies?: number[]
  error?: string
}

export interface SectorInfo {
  naics: string
  sector: string
  factor: number
}

export const mlAPI = {
  // ML Health Check
  health: async () => {
    const response = await api.get('/api/v1/ml/health')
    return response.data
  },
  
  // Sector Benchmark
  benchmark: async (data: BenchmarkRequest): Promise<BenchmarkResponse> => {
    const response = await api.post('/api/v1/ml/benchmark', data)
    return response.data
  },
  
  // Target Pathway
  generateTarget: async (data: TargetRequest): Promise<TargetResponse> => {
    const response = await api.post('/api/v1/ml/target', data)
    return response.data
  },
  
  // Anomaly Detection
  detectAnomalies: async (data: AnomalyRequest): Promise<AnomalyResponse> => {
    const response = await api.post('/api/v1/ml/anomaly', data)
    return response.data
  },
  
  // Get Sector List
  getSectors: async (): Promise<{ success: boolean; sectors: SectorInfo[]; total_count: number }> => {
    const response = await api.get('/api/v1/ml/sectors')
    return response.data
  },
  
  // Get SBTi Targets
  getSBTiTargets: async () => {
    const response = await api.get('/api/v1/ml/sbti-targets')
    return response.data
  },
  
  // Energy Forecast
  forecast: async (data: {
    data: Array<Record<string, any>>
    location?: string
    future_hours?: number
    include_weather?: boolean
  }): Promise<ForecastResponse> => {
    const response = await api.post('/api/v1/ml/forecast', data)
    return response.data
  },
  
  // AI Insights
  getAIInsights: async (tabType: string, data: Record<string, any>): Promise<{ success: boolean; insights?: string; error?: string }> => {
    const response = await api.post('/api/v1/ml/ai-insights', {
      tab_type: tabType,
      data: data
    })
    return response.data
  },
}

export interface ForecastRequest {
  data: Array<Record<string, any>>
  location?: string
  future_hours?: number
  include_weather?: boolean
}

export interface ForecastResponse {
  success: boolean
  predictions?: Array<{
    datetime: string
    predicted_power: number
  }>
  weather_features?: boolean
  error?: string
}

export default api

