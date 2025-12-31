'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Database, Filter, X, Check, Info, Lightbulb, BookOpen, ChevronDown, ChevronUp } from 'lucide-react'
import { activityAPI } from '@/services/api'

interface Activity {
  id: string
  name: string
  category: string
  scope: string
  region: string
  source?: string
}

interface ActivitySearchProps {
  onActivitySelect?: (activity: Activity) => void
  selectedActivity?: Activity | null
}

export default function ActivitySearch({ onActivitySelect, selectedActivity: propSelectedActivity }: ActivitySearchProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedScope, setSelectedScope] = useState<string>('all')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [results, setResults] = useState<Activity[]>([])
  const [suggestions, setSuggestions] = useState<Activity[]>([])
  const [loading, setLoading] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(propSelectedActivity || null)
  const [showInfoPanel, setShowInfoPanel] = useState(true)
  const searchInputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)

  // Sync with prop - only update if different to prevent loops
  useEffect(() => {
    // Only sync when prop changes, using a ref to track previous value
    if (propSelectedActivity !== null) {
      setSelectedActivity(propSelectedActivity)
    } else {
      setSelectedActivity(null)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [propSelectedActivity])

  // Debounced search for suggestions
  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSuggestions([])
      setShowSuggestions(false)
      return
    }

    const timeoutId = setTimeout(async () => {
      try {
        const response = await activityAPI.search(
          searchQuery,
          selectedScope !== 'all' ? selectedScope.replace('Scope ', '') : undefined,
          selectedCategory !== 'all' ? selectedCategory : undefined,
          undefined,
          10 // Limit suggestions to 10
        )
        setSuggestions(response.results || [])
        setShowSuggestions(true)
      } catch (err) {
        console.error('Suggestions error:', err)
        setSuggestions([])
      }
    }, 300) // 300ms debounce

    return () => clearTimeout(timeoutId)
  }, [searchQuery, selectedScope, selectedCategory])

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        searchInputRef.current &&
        !searchInputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setResults([])
      return
    }

    setLoading(true)
    setShowSuggestions(false)
    try {
      const response = await activityAPI.search(
        searchQuery,
        selectedScope !== 'all' ? selectedScope.replace('Scope ', '') : undefined,
        selectedCategory !== 'all' ? selectedCategory : undefined
      )
      setResults(response.results || [])
    } catch (err: any) {
      console.error('Search error:', err)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const handleSelectSuggestion = (activity: Activity) => {
    setSearchQuery(activity.name)
    setShowSuggestions(false)
    setResults([activity])
    setSelectedActivity(activity)
  }

  const handleUseActivity = (activity: Activity) => {
    setSelectedActivity(activity)
    // Call parent callback to switch to calculator tab
    if (onActivitySelect) {
      onActivitySelect(activity)
    } else {
      // Fallback: scroll to selected activity info
      setTimeout(() => {
        const element = document.getElementById('selected-activity-info')
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
        }
      }, 100)
    }
  }

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {/* Main Search Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-8 shadow-xl md:col-span-2"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-forest-100 rounded-lg">
              <Database className="w-6 h-6 text-forest-600" />
            </div>
            <h2 className="text-2xl font-display text-forest-700">Activity Database</h2>
          </div>
        </div>

      <div className="space-y-4">
        {/* Search Input with Autocomplete */}
        <div className="relative">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  setSelectedActivity(null)
                }}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                onFocus={() => {
                  if (suggestions.length > 0) setShowSuggestions(true)
                }}
                placeholder="Emisyon aktivitelerini arayın (örn: electricity, diesel, fuel)..."
                className="w-full px-4 py-3 rounded-lg border border-sage-200 focus:border-forest-500 focus:ring-2 focus:ring-forest-200 transition-all"
              />
              
              {/* Suggestions Dropdown */}
              <AnimatePresence>
                {showSuggestions && suggestions.length > 0 && (
                  <motion.div
                    ref={suggestionsRef}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute z-50 w-full mt-2 bg-white border border-sage-200 rounded-lg shadow-xl max-h-64 overflow-y-auto"
                  >
                    {suggestions.map((activity, index) => (
                      <motion.div
                        key={`suggestion-${activity.id}-${index}-${activity.name}`}
                        onClick={() => handleSelectSuggestion(activity)}
                        className="p-3 hover:bg-forest-50 cursor-pointer border-b border-sage-100 last:border-b-0 transition-colors"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-sage-700 text-sm">{activity.name}</p>
                            <div className="flex gap-2 mt-1">
                              <span className="text-xs px-2 py-0.5 bg-forest-100 text-forest-700 rounded">
                                {activity.scope}
                              </span>
                              <span className="text-xs px-2 py-0.5 bg-sage-100 text-sage-700 rounded">
                                {activity.category}
                              </span>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            <button
              onClick={handleSearch}
              disabled={loading || !searchQuery.trim()}
              className="px-6 py-3 bg-forest-600 hover:bg-forest-700 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Search className="w-5 h-5" />
              Ara
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-sage-700 mb-2">
              <Filter className="w-4 h-4 inline mr-1" />
              Kapsam
            </label>
            <select
              value={selectedScope}
              onChange={(e) => setSelectedScope(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-sage-200 focus:border-forest-500 focus:ring-2 focus:ring-forest-200"
            >
              <option value="all">Tüm Kapsamlar</option>
              <option value="Scope 1">Scope 1</option>
              <option value="Scope 2">Scope 2</option>
              <option value="Scope 3">Scope 3</option>
            </select>
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-sage-700 mb-2">
              Kategori
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-sage-200 focus:border-forest-500 focus:ring-2 focus:ring-forest-200"
            >
              <option value="all">Tüm Kategoriler</option>
              <option value="Energy">Enerji</option>
              <option value="Transportation">Ulaşım</option>
              <option value="Waste">Atık</option>
            </select>
          </div>
        </div>

        {/* Results */}
        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-forest-600"></div>
            <p className="mt-2 text-sm text-sage-600">Aranıyor...</p>
          </div>
        )}

        {results.length > 0 && (
          <div className="space-y-2 mt-4">
            {results.map((activity, index) => (
              <motion.div
                key={`${activity.id}-${index}-${activity.name}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-white border border-sage-200 rounded-lg hover:border-forest-300 transition-all cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-sage-700">{activity.name}</p>
                    <div className="flex gap-2 mt-1">
                      <span className="text-xs px-2 py-1 bg-forest-100 text-forest-700 rounded">
                        {activity.scope}
                      </span>
                      <span className="text-xs px-2 py-1 bg-sage-100 text-sage-700 rounded">
                        {activity.category}
                      </span>
                      <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                        {activity.region}
                      </span>
                    </div>
                  </div>
                  <button 
                    onClick={() => handleUseActivity(activity)}
                    className="px-4 py-2 bg-forest-600 hover:bg-forest-700 text-white text-sm rounded-lg transition-all flex items-center gap-2"
                  >
                    <Check className="w-4 h-4" />
                    Kullan
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {!loading && results.length === 0 && searchQuery && (
          <div className="text-center py-8 text-sage-500">
            <p>Aktivite bulunamadı. Farklı bir arama terimi deneyin.</p>
            <p className="text-xs mt-2">Deneyin: "diesel", "electricity", "fuel", "transport", "natural gas"</p>
          </div>
        )}

        {/* Selected Activity Info */}
        {selectedActivity && (
          <motion.div
            id="selected-activity-info"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 bg-forest-50 border-2 border-forest-300 rounded-lg shadow-md"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Check className="w-5 h-5 text-forest-600" />
                  <p className="font-semibold text-forest-700">Aktivite Seçildi</p>
                </div>
                <p className="text-sage-700 font-medium mb-2">{selectedActivity.name}</p>
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
                <p className="text-xs text-sage-600 mt-3">
                  💡 Calculator sekmesine geçiliyor...
                </p>
              </div>
              <button
                onClick={() => setSelectedActivity(null)}
                className="ml-4 p-2 hover:bg-forest-200 rounded-lg transition-colors"
                title="Seçimi temizle"
              >
                <X className="w-4 h-4 text-forest-600" />
              </button>
            </div>
          </motion.div>
        )}
      </div>
      </motion.div>

      {/* Info Panel */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="glass rounded-2xl shadow-xl overflow-hidden"
      >
        <button
          onClick={() => setShowInfoPanel(!showInfoPanel)}
          className="w-full p-4 bg-forest-50 hover:bg-forest-100 transition-colors flex items-center justify-between"
        >
          <div className="flex items-center gap-2">
            <Info className="w-5 h-5 text-forest-600" />
            <h3 className="font-semibold text-forest-700">Nasıl Kullanılır?</h3>
          </div>
          {showInfoPanel ? (
            <ChevronUp className="w-5 h-5 text-forest-600" />
          ) : (
            <ChevronDown className="w-5 h-5 text-forest-600" />
          )}
        </button>

        <AnimatePresence>
          {showInfoPanel && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="p-6 space-y-6">
                {/* Purpose */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <BookOpen className="w-4 h-4 text-forest-600" />
                    <h4 className="font-semibold text-forest-700">Bu Nedir?</h4>
                  </div>
                  <p className="text-sm text-sage-600 leading-relaxed">
                    Veritabanından 270,000+ emisyon faktörünü arayın. Karbon ayak izi hesaplamalarınız için doğru aktiviteyi bulun.
                  </p>
                </div>

                {/* How to Use */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Lightbulb className="w-4 h-4 text-forest-600" />
                    <h4 className="font-semibold text-forest-700">Kullanım Adımları</h4>
                  </div>
                  <ol className="text-sm text-sage-600 space-y-2 list-decimal list-inside">
                    <li>Arama kutusuna anahtar kelimeler yazın (örn: "diesel", "electricity")</li>
                    <li>Otomatik önerilerden seçin veya Enter'a basın</li>
                    <li>Gerekirse Scope veya Kategori ile filtreleyin</li>
                    <li>Bir aktivite seçmek için "Use" butonuna tıklayın</li>
                    <li>Kullanmak için Calculator sekmesine geçin</li>
                  </ol>
                </div>

                {/* Popular Searches */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Search className="w-4 h-4 text-forest-600" />
                    <h4 className="font-semibold text-forest-700">Popüler Aramalar</h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {['diesel', 'electricity', 'natural gas', 'fuel', 'transport', 'coal', 'petrol', 'lpg', 'heating', 'waste'].map((term) => (
                      <button
                        key={term}
                        onClick={async () => {
                          setSearchQuery(term)
                          // Search directly with the term instead of using state
                          setLoading(true)
                          try {
                            const response = await activityAPI.search(term, undefined, undefined)
                            setResults(response.results || [])
                          } catch (err) {
                            console.error('Search error:', err)
                            setResults([])
                          } finally {
                            setLoading(false)
                          }
                        }}
                        className="px-3 py-1.5 text-xs bg-sage-100 hover:bg-forest-100 text-sage-700 hover:text-forest-700 rounded-full transition-colors"
                      >
                        {term}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Tips */}
                <div className="p-4 bg-forest-50 rounded-lg border border-forest-200">
                  <p className="text-xs text-forest-700 font-medium mb-2">💡 İpucu</p>
                  <p className="text-xs text-sage-600">
                    Daha iyi sonuçlar için "diesel van" veya "electricity grid" gibi spesifik terimler kullanın. Veritabanı Scope 1, 2 ve 3 aktivitelerini içerir.
                  </p>
                </div>

                {/* Scope Info */}
                <div className="pt-4 border-t border-sage-200">
                  <p className="text-xs font-semibold text-sage-700 mb-2">Scope Kategorileri:</p>
                  <div className="space-y-1.5 text-xs text-sage-600">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-forest-500 rounded-full"></span>
                      <span><strong>Scope 1:</strong> Doğrudan emisyonlar</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-sage-500 rounded-full"></span>
                      <span><strong>Scope 2:</strong> Dolaylı emisyonlar (enerji)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                      <span><strong>Scope 3:</strong> Diğer dolaylı emisyonlar</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  )
}

