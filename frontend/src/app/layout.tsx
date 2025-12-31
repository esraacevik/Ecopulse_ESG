import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ECOLOGIA - ESG Carbon Calculator',
  description: 'AI-Powered Carbon Footprint Calculation & ESG Reporting Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

