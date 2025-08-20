// 🏗️ MIT Logistics Frontend - Root Layout

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from '@/components/ui/toaster'
import { GlobalHeader } from '@/components/layout/GlobalHeader'
import '@/styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'MIT Logistics - Sistema de Logística Inteligente',
  description: 'Dashboard para teste de agentes de IA especializados em logística - transformando dados em inteligência',
  keywords: 'logística, inteligência artificial, agentes, CT-e, containers, rastreamento',
  authors: [{ name: 'MIT Logistics Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'noindex, nofollow', // Development only
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR" data-theme="light">
      <body className={inter.className}>
        <div id="root">
          <GlobalHeader />
          {children}
        </div>
        <div id="modal-root" />
        <Toaster />
      </body>
    </html>
  )
}