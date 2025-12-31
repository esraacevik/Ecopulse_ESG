'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FileText, Download, Trash2, Search, Calendar, Building2 } from 'lucide-react'
import { reportAPI } from '@/services/api'

interface ReportInfo {
  filename: string
  company_name: string
  period: string
  created_at: string
  file_size: number
  file_path: string
}

export default function ReportHistory() {
  const [reports, setReports] = useState<ReportInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [deleting, setDeleting] = useState<string | null>(null)

  useEffect(() => {
    loadReports()
  }, [])

  const loadReports = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await reportAPI.list()
      if (response.success) {
        setReports(response.reports || [])
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Raporlar yüklenirken hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (filename: string) => {
    if (!confirm(`Bu raporu silmek istediğinize emin misiniz?`)) {
      return
    }

    try {
      setDeleting(filename)
      await reportAPI.delete(filename)
      await loadReports() // Reload list
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Rapor silinirken hata oluştu')
    } finally {
      setDeleting(null)
    }
  }

  const handleDownload = (filename: string) => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const url = `${API_URL}/api/v1/report/download/${encodeURIComponent(filename)}`
    window.open(url, '_blank')
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('tr-TR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateString
    }
  }

  const filteredReports = reports.filter(report => {
    const searchLower = searchTerm.toLowerCase()
    return (
      report.company_name.toLowerCase().includes(searchLower) ||
      report.period.toLowerCase().includes(searchLower) ||
      report.filename.toLowerCase().includes(searchLower)
    )
  })

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="glass rounded-xl p-8 text-center"
      >
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-forest-600 mx-auto"></div>
        <p className="mt-4 text-forest-600">Raporlar yükleniyor...</p>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-xl p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-forest-100 rounded-lg">
            <FileText className="w-5 h-5 text-forest-600" />
          </div>
          <h2 className="text-2xl font-display text-forest-700">Rapor Geçmişi</h2>
          <span className="text-sm text-forest-500 bg-forest-50 px-2 py-1 rounded">
            {reports.length} rapor
          </span>
        </div>
        <button
          onClick={loadReports}
          className="px-4 py-2 bg-forest-600 text-white rounded-lg hover:bg-forest-700 transition"
        >
          Yenile
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Search */}
      <div className="mb-6 relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-forest-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Şirket adı, dönem veya dosya adı ile ara..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-forest-200 rounded-lg focus:ring-2 focus:ring-forest-500 focus:border-transparent"
        />
      </div>

      {/* Reports List */}
      {filteredReports.length === 0 ? (
        <div className="text-center py-12 text-forest-500">
          <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg">
            {searchTerm ? 'Arama sonucu bulunamadı' : 'Henüz rapor oluşturulmamış'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredReports.map((report) => (
            <motion.div
              key={report.filename}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white rounded-lg border border-forest-200 p-4 hover:shadow-md transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <FileText className="w-5 h-5 text-forest-600" />
                    <h3 className="font-semibold text-forest-700">{report.filename}</h3>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-forest-600">
                    <div className="flex items-center gap-2">
                      <Building2 className="w-4 h-4" />
                      <span>{report.company_name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      <span>{report.period}</span>
                    </div>
                    <div>
                      <span>{formatDate(report.created_at)}</span>
                      <span className="ml-2 text-forest-400">• {formatFileSize(report.file_size)}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => handleDownload(report.filename)}
                    className="p-2 text-forest-600 hover:bg-forest-50 rounded-lg transition"
                    title="İndir"
                  >
                    <Download className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(report.filename)}
                    disabled={deleting === report.filename}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition disabled:opacity-50"
                    title="Sil"
                  >
                    {deleting === report.filename ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-red-600"></div>
                    ) : (
                      <Trash2 className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  )
}

