'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Calculator, Leaf, X, Database } from 'lucide-react'
import { emissionAPI, EmissionInput } from '@/services/api'

interface SelectedActivity {
  id: string
  name: string
  category: string
  scope: string
  region: string
  source?: string
}

interface EmissionFormProps {
  onCalculate: (results: any) => void
  selectedActivity?: SelectedActivity | null
  onActivityClear?: () => void
  prefilledData?: Partial<EmissionInput> | null
  onPrefilledDataUsed?: () => void
}

export default function EmissionForm({ onCalculate, selectedActivity, onActivityClear, prefilledData, onPrefilledDataUsed }: EmissionFormProps) {
  const [formData, setFormData] = useState<EmissionInput>({
    category: 'Enerji',
    // Scope 1 - Direct
    natural_gas_m3: 0,
    diesel_litre: 0,
    petrol_litre: 0,
    lpg_litre: 0,
    coal_kg: 0,
    fuel_oil_litre: 0,
    biogas_kwh: 0,
    refrigerant_kg: 0,
    vehicle_km: 0,
    vehicle_fuel_type: 'Dizel',
    // Scope 2 - Indirect Energy
    electricity_kwh: 0,
    heating_kwh: 0,
    cooling_kwh: 0,
    // Scope 3 - Value Chain
    water_litre: 0,
    waste_kg: 0,
    waste_type: 'landfill',
    flight_km: 0,
    flight_class: 'Ekonomi',
    hotel_nights: 0,
    taxi_km: 0,
    train_km: 0,
    bus_km: 0,
    metro_km: 0,
    freight_ton_km: 0,
    paper_kg: 0,
    // Settings
    region: 'TR',
    period: 'Monthly',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showInvoiceLoaded, setShowInvoiceLoaded] = useState(false)

  // Update region when activity is selected
  useEffect(() => {
    if (selectedActivity) {
      // Map region codes
      const regionMap: Record<string, string> = {
        'GB': 'GB',
        'US': 'US',
        'TR': 'TR',
        'GLOBAL': 'GLOBAL',
      }
      const mappedRegion = regionMap[selectedActivity.region] || selectedActivity.region || 'TR'
      setFormData(prev => ({ ...prev, region: mappedRegion }))
    }
  }, [selectedActivity])

  // Handle prefilled data from Invoice Scanner
  useEffect(() => {
    if (prefilledData) {
      setFormData(prev => ({
        ...prev,
        electricity_kwh: prefilledData.electricity_kwh || prev.electricity_kwh,
        natural_gas_m3: prefilledData.natural_gas_m3 || prev.natural_gas_m3,
        water_litre: prefilledData.water_litre || prev.water_litre,
      }))
      // Show banner
      setShowInvoiceLoaded(true)
      // Mark prefilled data as used
      if (onPrefilledDataUsed) {
        onPrefilledDataUsed()
      }
      // Hide banner after 5 seconds
      setTimeout(() => setShowInvoiceLoaded(false), 5000)
    }
  }, [prefilledData, onPrefilledDataUsed])

  // Determine which field is relevant based on activity name
  const getRelevantFieldHint = () => {
    if (!selectedActivity) return null
    
    const nameLower = selectedActivity.name.toLowerCase()
    const categoryLower = selectedActivity.category?.toLowerCase() || ''
    
    // Scope 1
    if (nameLower.includes('diesel') || nameLower.includes('dizel')) {
      return { field: 'diesel_litre', label: 'Diesel Tüketimi (litre)', icon: '⛽' }
    }
    if (nameLower.includes('petrol') || nameLower.includes('gasoline') || nameLower.includes('benzin')) {
      return { field: 'petrol_litre', label: 'Petrol Tüketimi (litre)', icon: '⛽' }
    }
    if (nameLower.includes('natural gas') || nameLower.includes('doğal gaz') || (nameLower.includes('gas') && !nameLower.includes('gasoline') && !nameLower.includes('biogas'))) {
      return { field: 'natural_gas_m3', label: 'Doğal Gaz Tüketimi (m³)', icon: '🔥' }
    }
    if (nameLower.includes('lpg')) {
      return { field: 'lpg_litre', label: 'LPG Tüketimi (litre)', icon: '⛽' }
    }
    if (nameLower.includes('coal') || nameLower.includes('kömür')) {
      return { field: 'coal_kg', label: 'Kömür Tüketimi (kg)', icon: '🪨' }
    }
    if (nameLower.includes('fuel oil') || nameLower.includes('fuel-oil') || nameLower.includes('distillate')) {
      return { field: 'fuel_oil_litre', label: 'Fuel Oil (litre)', icon: '🛢️' }
    }
    if (nameLower.includes('biogas') || nameLower.includes('biyogaz')) {
      return { field: 'biogas_kwh', label: 'Biyogaz (kWh)', icon: '🌿' }
    }
    if (nameLower.includes('refrigerant') || nameLower.includes('hfc') || nameLower.includes('r-134a') || nameLower.includes('r-410a')) {
      return { field: 'refrigerant_kg', label: 'Soğutucu Gaz Kaçağı (kg)', icon: '❄️' }
    }
    if (categoryLower.includes('transport') || categoryLower.includes('ulaşım') || nameLower.includes('vehicle') || nameLower.includes('araç')) {
      return { field: 'vehicle_km', label: 'Araç Yolculuğu (km)', icon: '🚗' }
    }
    // Scope 2
    if (nameLower.includes('electricity') || nameLower.includes('elektrik')) {
      return { field: 'electricity_kwh', label: 'Elektrik Tüketimi (kWh)', icon: '⚡' }
    }
    if (nameLower.includes('heating') || nameLower.includes('ısıtma') || nameLower.includes('district heat')) {
      return { field: 'heating_kwh', label: 'Merkezi Isıtma (kWh)', icon: '🌡️' }
    }
    if (nameLower.includes('cooling') || nameLower.includes('soğutma') || nameLower.includes('chiller')) {
      return { field: 'cooling_kwh', label: 'Merkezi Soğutma (kWh)', icon: '❄️' }
    }
    // Scope 3
    if (nameLower.includes('water') || nameLower.includes('su')) {
      return { field: 'water_litre', label: 'Su Tüketimi (litre)', icon: '💧' }
    }
    if (nameLower.includes('waste') || nameLower.includes('atık') || nameLower.includes('landfill') || nameLower.includes('incineration')) {
      return { field: 'waste_kg', label: 'Atık (kg)', icon: '🗑️' }
    }
    if (nameLower.includes('flight') || nameLower.includes('uçak') || nameLower.includes('aviation')) {
      return { field: 'flight_km', label: 'Uçak Yolculuğu (km)', icon: '✈️' }
    }
    if (nameLower.includes('hotel') || nameLower.includes('accommodation') || nameLower.includes('otel') || nameLower.includes('konaklama')) {
      return { field: 'hotel_nights', label: 'Otel Konaklama (gece)', icon: '🏨' }
    }
    if (nameLower.includes('taxi') || nameLower.includes('taksi')) {
      return { field: 'taxi_km', label: 'Taksi (km)', icon: '🚕' }
    }
    if (nameLower.includes('train') || nameLower.includes('tren') || nameLower.includes('rail')) {
      return { field: 'train_km', label: 'Tren (km)', icon: '🚆' }
    }
    if (nameLower.includes('bus') || nameLower.includes('otobüs')) {
      return { field: 'bus_km', label: 'Otobüs (km)', icon: '🚌' }
    }
    if (nameLower.includes('subway') || nameLower.includes('metro')) {
      return { field: 'metro_km', label: 'Metro (km)', icon: '🚇' }
    }
    if (nameLower.includes('freight') || nameLower.includes('cargo') || nameLower.includes('kargo') || nameLower.includes('nakliye')) {
      return { field: 'freight_ton_km', label: 'Kargo (ton-km)', icon: '📦' }
    }
    if (nameLower.includes('paper') || nameLower.includes('kağıt') || nameLower.includes('pulp')) {
      return { field: 'paper_kg', label: 'Kağıt Tüketimi (kg)', icon: '📄' }
    }
    
    return null
  }

  const relevantField = getRelevantFieldHint()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      console.log('Submitting form data:', formData)
      const results = await emissionAPI.calculate(formData)
      console.log('Calculation results:', results)
      onCalculate(results)
    } catch (err: any) {
      console.error('Calculation error:', err)
      const errorMessage = err.response?.data?.detail || err.message || 'An error occurred'
      setError(errorMessage)
      onCalculate(null) // Clear results on error
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-8 shadow-xl card-hover"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-forest-100 rounded-lg">
          <Calculator className="w-6 h-6 text-forest-600" />
        </div>
        <h2 className="text-2xl font-display text-forest-700">Emission Calculator</h2>
      </div>

      {/* Invoice Data Loaded Banner */}
      {showInvoiceLoaded && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="mb-6 p-4 bg-blue-50 border-2 border-blue-300 rounded-lg"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-2xl">📄</span>
              <div>
                <p className="font-semibold text-blue-700">Fatura Verileri Yüklendi!</p>
                <p className="text-sm text-blue-600">
                  Elektrik, doğalgaz ve/veya su tüketim verileri form alanlarına aktarıldı.
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowInvoiceLoaded(false)}
              className="p-1 hover:bg-blue-100 rounded"
            >
              <X className="w-4 h-4 text-blue-600" />
            </button>
          </div>
        </motion.div>
      )}

      {/* Selected Activity Banner */}
      {selectedActivity && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-forest-50 border-2 border-forest-300 rounded-lg"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Database className="w-4 h-4 text-forest-600" />
                <p className="font-semibold text-forest-700 text-sm">Veritabanından Seçilen Aktivite</p>
              </div>
              <p className="text-sage-700 font-medium text-sm mb-2">{selectedActivity.name}</p>
              <div className="flex gap-2 flex-wrap">
                <span className="text-xs px-2 py-1 bg-forest-100 text-forest-700 rounded">
                  {selectedActivity.scope}
                </span>
                <span className="text-xs px-2 py-1 bg-sage-100 text-sage-700 rounded">
                  {selectedActivity.category}
                </span>
                <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                  {selectedActivity.region}
                </span>
              </div>
              <p className="text-xs text-sage-600 mt-2">
                <strong>Otomatik doldurulan:</strong> Bölge (Region) aktiviteye göre ayarlandı.
              </p>
              <p className="text-xs text-sage-500 mt-1">
                <strong>Manuel girmeniz gereken:</strong> Aşağıdaki formdan ilgili tüketim miktarını girin (örn: litre, kWh, m³).
              </p>
            </div>
            {onActivityClear && (
              <button
                onClick={onActivityClear}
                className="ml-4 p-2 hover:bg-forest-200 rounded-lg transition-colors"
                title="Clear activity"
              >
                <X className="w-4 h-4 text-forest-600" />
              </button>
            )}
          </div>
        </motion.div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* ========== SCOPE 1: Doğrudan Emisyonlar ========== */}
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
          <div className="flex items-center gap-2 mb-4">
            <span className="px-2 py-1 bg-red-200 text-red-800 text-xs font-bold rounded">SCOPE 1</span>
            <h3 className="text-lg font-semibold text-red-800">🔥 Doğrudan Emisyonlar</h3>
          </div>
          <p className="text-xs text-red-700 mb-4">Şirket kontrolündeki yakıt yanması ve araç emisyonları</p>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                Doğalgaz (m³)
                {relevantField?.field === 'natural_gas_m3' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.natural_gas_m3}
                onChange={(e) => setFormData({ ...formData, natural_gas_m3: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'natural_gas_m3' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                Dizel (litre)
                {relevantField?.field === 'diesel_litre' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.diesel_litre}
                onChange={(e) => setFormData({ ...formData, diesel_litre: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'diesel_litre' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                Benzin (litre)
                {relevantField?.field === 'petrol_litre' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.petrol_litre}
                onChange={(e) => setFormData({ ...formData, petrol_litre: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'petrol_litre' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                LPG (litre)
                {relevantField?.field === 'lpg_litre' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.lpg_litre}
                onChange={(e) => setFormData({ ...formData, lpg_litre: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'lpg_litre' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                Kömür (kg)
                {relevantField?.field === 'coal_kg' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.coal_kg}
                onChange={(e) => setFormData({ ...formData, coal_kg: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'coal_kg' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                🛢️ Fuel Oil (litre)
                {relevantField?.field === 'fuel_oil_litre' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.fuel_oil_litre}
                onChange={(e) => setFormData({ ...formData, fuel_oil_litre: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'fuel_oil_litre' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                🌿 Biyogaz (kWh)
                {relevantField?.field === 'biogas_kwh' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.biogas_kwh}
                onChange={(e) => setFormData({ ...formData, biogas_kwh: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'biogas_kwh' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                ❄️ Soğutucu Gaz Kaçağı (kg)
                {relevantField?.field === 'refrigerant_kg' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.refrigerant_kg}
                onChange={(e) => setFormData({ ...formData, refrigerant_kg: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'refrigerant_kg' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="R-134a, R-410a vb."
              />
              <p className="text-xs text-red-600 mt-1 italic">Klima/buzdolabı bakım kaynaklı kaçaklar (GWP: 1430)</p>
            </div>
          </div>

          {/* Şirket Araçları */}
          <div className="mt-4 pt-4 border-t border-red-200">
            <p className="text-sm font-medium text-red-800 mb-3">🚗 Şirket Araçları</p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">Mesafe (km)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.vehicle_km}
                  onChange={(e) => setFormData({ ...formData, vehicle_km: parseFloat(e.target.value) || 0 })}
                  className="w-full px-4 py-3 rounded-lg border border-sage-200 bg-white focus:border-forest-500 focus:ring-2 focus:ring-forest-200 transition-all"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">Yakıt Tipi</label>
                <select
                  value={formData.vehicle_fuel_type}
                  onChange={(e) => setFormData({ ...formData, vehicle_fuel_type: e.target.value })}
                  className="w-full px-4 py-3 rounded-lg border border-sage-200 bg-white focus:border-forest-500 focus:ring-2 focus:ring-forest-200 transition-all"
                >
                  <option value="Dizel">Dizel</option>
                  <option value="Benzin">Benzin</option>
                  <option value="Elektrikli">Elektrikli</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* ========== SCOPE 2: Dolaylı Enerji Emisyonları ========== */}
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
          <div className="flex items-center gap-2 mb-4">
            <span className="px-2 py-1 bg-yellow-200 text-yellow-800 text-xs font-bold rounded">SCOPE 2</span>
            <h3 className="text-lg font-semibold text-yellow-800">⚡ Dolaylı Enerji Emisyonları</h3>
          </div>
          <p className="text-xs text-yellow-700 mb-4">Satın alınan elektrik, ısıtma ve soğutma kaynaklı emisyonlar</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                Elektrik (kWh)
                {relevantField?.field === 'electricity_kwh' && (
                  <span className="ml-1 text-xs text-forest-600">✓</span>
                )}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.electricity_kwh}
                onChange={(e) => setFormData({ ...formData, electricity_kwh: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'electricity_kwh' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                Merkezi Isıtma (kWh)
                {relevantField?.field === 'heating_kwh' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.heating_kwh}
                onChange={(e) => setFormData({ ...formData, heating_kwh: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'heating_kwh' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                Merkezi Soğutma (kWh)
                {relevantField?.field === 'cooling_kwh' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.cooling_kwh}
                onChange={(e) => setFormData({ ...formData, cooling_kwh: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'cooling_kwh' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>
          </div>
          
          <p className="text-xs text-yellow-600 mt-3 italic">
            💡 Merkezi ısıtma/soğutma için EU/US proxy faktörleri kullanılmaktadır.
          </p>
        </div>

        {/* ========== SCOPE 3: Diğer Dolaylı Emisyonlar ========== */}
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
          <div className="flex items-center gap-2 mb-4">
            <span className="px-2 py-1 bg-blue-200 text-blue-800 text-xs font-bold rounded">SCOPE 3</span>
            <h3 className="text-lg font-semibold text-blue-800">🌍 Diğer Dolaylı Emisyonlar</h3>
          </div>
          <p className="text-xs text-blue-700 mb-4">Değer zinciri: iş seyahatleri, su, atık ve tedarik zinciri</p>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                Su Tüketimi (litre)
                {relevantField?.field === 'water_litre' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.water_litre}
                onChange={(e) => setFormData({ ...formData, water_litre: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'water_litre' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                Atık (kg)
                {relevantField?.field === 'waste_kg' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.waste_kg}
                onChange={(e) => setFormData({ ...formData, waste_kg: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'waste_kg' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">Atık Tipi</label>
              <select
                value={formData.waste_type}
                onChange={(e) => setFormData({ ...formData, waste_type: e.target.value })}
                className="w-full px-4 py-3 rounded-lg border border-sage-200 bg-white focus:border-forest-500 focus:ring-2 focus:ring-forest-200 transition-all"
              >
                <option value="landfill">🏭 Düzenli Depolama (Landfill)</option>
                <option value="recycling">♻️ Geri Dönüşüm</option>
                <option value="incineration">🔥 Yakma</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                📄 Kağıt Tüketimi (kg)
                {relevantField?.field === 'paper_kg' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.paper_kg}
                onChange={(e) => setFormData({ ...formData, paper_kg: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'paper_kg' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-2">
                📦 Kargo/Nakliye (ton-km)
                {relevantField?.field === 'freight_ton_km' && <span className="ml-1 text-xs text-forest-600">✓</span>}
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.freight_ton_km}
                onChange={(e) => setFormData({ ...formData, freight_ton_km: parseFloat(e.target.value) || 0 })}
                className={`w-full px-4 py-3 rounded-lg border transition-all ${
                  relevantField?.field === 'freight_ton_km' 
                    ? 'border-forest-400 bg-forest-50' 
                    : 'border-sage-200 bg-white'
                } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                placeholder="0.00"
              />
            </div>
          </div>

          {/* İş Seyahatleri */}
          <div className="mt-4 pt-4 border-t border-blue-200">
            <p className="text-sm font-medium text-blue-800 mb-3">✈️ İş Seyahatleri</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">Uçuş (km)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.flight_km}
                  onChange={(e) => setFormData({ ...formData, flight_km: parseFloat(e.target.value) || 0 })}
                  className="w-full px-4 py-3 rounded-lg border border-sage-200 bg-white focus:border-forest-500 focus:ring-2 focus:ring-forest-200 transition-all"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">Uçuş Sınıfı</label>
                <select
                  value={formData.flight_class}
                  onChange={(e) => setFormData({ ...formData, flight_class: e.target.value })}
                  className="w-full px-4 py-3 rounded-lg border border-sage-200 bg-white focus:border-forest-500 focus:ring-2 focus:ring-forest-200 transition-all"
                >
                  <option value="Ekonomi">Ekonomi</option>
                  <option value="Business">Business</option>
                  <option value="First Class">First Class</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  🏨 Otel (gece)
                  {relevantField?.field === 'hotel_nights' && <span className="ml-1 text-xs text-forest-600">✓</span>}
                </label>
                <input
                  type="number"
                  step="1"
                  value={formData.hotel_nights}
                  onChange={(e) => setFormData({ ...formData, hotel_nights: parseFloat(e.target.value) || 0 })}
                  className={`w-full px-4 py-3 rounded-lg border transition-all ${
                    relevantField?.field === 'hotel_nights' 
                      ? 'border-forest-400 bg-forest-50' 
                      : 'border-sage-200 bg-white'
                  } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                  placeholder="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  🚕 Taksi (km)
                  {relevantField?.field === 'taxi_km' && <span className="ml-1 text-xs text-forest-600">✓</span>}
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.taxi_km}
                  onChange={(e) => setFormData({ ...formData, taxi_km: parseFloat(e.target.value) || 0 })}
                  className={`w-full px-4 py-3 rounded-lg border transition-all ${
                    relevantField?.field === 'taxi_km' 
                      ? 'border-forest-400 bg-forest-50' 
                      : 'border-sage-200 bg-white'
                  } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                  placeholder="0.00"
                />
              </div>
            </div>
          </div>

          {/* Çalışan Ulaşımı */}
          <div className="mt-4 pt-4 border-t border-blue-200">
            <p className="text-sm font-medium text-blue-800 mb-3">🚇 Çalışan Ulaşımı (Commuting)</p>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  🚆 Tren (km)
                  {relevantField?.field === 'train_km' && <span className="ml-1 text-xs text-forest-600">✓</span>}
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.train_km}
                  onChange={(e) => setFormData({ ...formData, train_km: parseFloat(e.target.value) || 0 })}
                  className={`w-full px-4 py-3 rounded-lg border transition-all ${
                    relevantField?.field === 'train_km' 
                      ? 'border-forest-400 bg-forest-50' 
                      : 'border-sage-200 bg-white'
                  } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  🚇 Metro (km)
                  {relevantField?.field === 'metro_km' && <span className="ml-1 text-xs text-forest-600">✓</span>}
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.metro_km}
                  onChange={(e) => setFormData({ ...formData, metro_km: parseFloat(e.target.value) || 0 })}
                  className={`w-full px-4 py-3 rounded-lg border transition-all ${
                    relevantField?.field === 'metro_km' 
                      ? 'border-forest-400 bg-forest-50' 
                      : 'border-sage-200 bg-white'
                  } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  🚌 Otobüs (km)
                  {relevantField?.field === 'bus_km' && <span className="ml-1 text-xs text-forest-600">✓</span>}
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.bus_km}
                  onChange={(e) => setFormData({ ...formData, bus_km: parseFloat(e.target.value) || 0 })}
                  className={`w-full px-4 py-3 rounded-lg border transition-all ${
                    relevantField?.field === 'bus_km' 
                      ? 'border-forest-400 bg-forest-50' 
                      : 'border-sage-200 bg-white'
                  } focus:border-forest-500 focus:ring-2 focus:ring-forest-200`}
                  placeholder="0.00"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Bölge Seçimi */}
        <div className="p-4 bg-sage-50 border border-sage-200 rounded-xl">
          <label className="block text-sm font-medium text-sage-700 mb-2">
            📍 Bölge / Ülke
          </label>
          <select
            value={formData.region}
            onChange={(e) => setFormData({ ...formData, region: e.target.value })}
            className="w-full px-4 py-3 rounded-lg border border-sage-200 bg-white focus:border-forest-500 focus:ring-2 focus:ring-forest-200 transition-all"
          >
            <option value="TR">🇹🇷 Türkiye</option>
            <option value="US">🇺🇸 Amerika</option>
            <option value="GB">🇬🇧 İngiltere</option>
            <option value="GLOBAL">🌍 Global</option>
          </select>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || (
            // Scope 1
            formData.natural_gas_m3 === 0 && 
            formData.diesel_litre === 0 && 
            formData.petrol_litre === 0 && 
            formData.lpg_litre === 0 && 
            formData.coal_kg === 0 &&
            formData.fuel_oil_litre === 0 &&
            formData.biogas_kwh === 0 &&
            formData.refrigerant_kg === 0 &&
            formData.vehicle_km === 0 &&
            // Scope 2
            formData.electricity_kwh === 0 && 
            formData.heating_kwh === 0 &&
            formData.cooling_kwh === 0 &&
            // Scope 3
            formData.water_litre === 0 &&
            formData.waste_kg === 0 &&
            formData.flight_km === 0 &&
            formData.hotel_nights === 0 &&
            formData.taxi_km === 0 &&
            formData.train_km === 0 &&
            formData.bus_km === 0 &&
            formData.metro_km === 0 &&
            formData.freight_ton_km === 0 &&
            formData.paper_kg === 0
          )}
          className="w-full py-4 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
        >
          {loading ? (
            'Hesaplanıyor...'
          ) : (
            <>
              <Leaf className="w-5 h-5" />
              Emisyon Hesapla
            </>
          )}
        </button>
      </form>
    </motion.div>
  )
}

