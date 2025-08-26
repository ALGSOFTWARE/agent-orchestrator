// 🏠 MIT Logistics Frontend - Homepage

'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useCurrentUser } from '@/lib/store/auth'
import { AuthModal } from '@/components/auth/AuthModal'
import styles from '@/styles/modules/HomePage.module.css'

export default function HomePage() {
  const [showAuthModal, setShowAuthModal] = useState(false)
  const currentUser = useCurrentUser()
  
  return (
    <div className={`${styles.container} ${currentUser ? styles.containerWithHeader : ''}`}>
      {/* Hero Section */}
      <header className={styles.hero}>
        <div className={styles.heroContent}>
          <div className={styles.logo}>
            <h1 className={styles.title}>
              MIT <span className={styles.highlight}>Logistics</span>
            </h1>
            <p className={styles.tagline}>
              Transformando logística em inteligência real
            </p>
          </div>
          
          <p className={styles.description}>
            Dashboard interativo com agentes de IA especializados em logística. 
            Powered by OpenAI e Google Gemini com roteamento inteligente para consultas de CT-e, 
            rastreamento de containers e documentos de transporte.
          </p>

          <div className={styles.actions}>
            {currentUser ? (
              <Link href="/agents" className={styles.primaryButton}>
                🤖 Testar Agentes
              </Link>
            ) : (
              <button 
                onClick={() => setShowAuthModal(true)}
                className={styles.primaryButton}
              >
                🔐 Fazer Login
              </button>
            )}
            <Link href="/monitoring" className={styles.secondaryButton}>
              📊 Monitoramento
            </Link>
          </div>
        </div>

        <div className={styles.heroVisual}>
          <div className={styles.grid}>
            <div className={styles.gridItem}>
              <div className={styles.icon}>🚪</div>
              <h3>Gatekeeper</h3>
              <p>Controle de acesso e roteamento</p>
            </div>
            <div className={styles.gridItem}>
              <div className={styles.icon}>📦</div>
              <h3>MIT Tracking v2</h3>
              <p>OpenAI/Gemini • CT-e, containers</p>
            </div>
            <div className={styles.gridItem}>
              <div className={styles.icon}>💰</div>
              <h3>Finance Agent</h3>
              <p>Operações financeiras</p>
            </div>
            <div className={styles.gridItem}>
              <div className={styles.icon}>👑</div>
              <h3>Admin Agent</h3>
              <p>Supervisão e gerenciamento</p>
            </div>
          </div>
        </div>
      </header>

      {/* Features Section */}
      <section className={styles.features}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Funcionalidades do Dashboard</h2>
          
          <div className={styles.featureGrid}>
            <div className={styles.feature}>
              <div className={styles.featureIcon}>🔐</div>
              <h3>Simulador de Autenticação</h3>
              <p>Teste diferentes roles e permissões com o Gatekeeper Agent</p>
              {currentUser ? (
                <Link href="/agents" className={styles.featureLink}>
                  Experimentar →
                </Link>
              ) : (
                <button 
                  onClick={() => setShowAuthModal(true)}
                  className={styles.featureLink}
                  style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}
                >
                  Entrar primeiro →
                </button>
              )}
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>💬</div>
              <h3>Sandbox de Agentes</h3>
              <p>Teste e compare agentes OpenAI vs Gemini - Sandbox público</p>
              <Link href="/chat" className={styles.featureLink}>
                Abrir Sandbox →
              </Link>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>📈</div>
              <h3>Monitoramento em Tempo Real</h3>
              <p>Acompanhe métricas e status dos serviços</p>
              <Link href="/monitoring" className={styles.featureLink}>
                Monitorar →
              </Link>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>🔍</div>
              <h3>API Explorer</h3>
              <p>Explore GraphQL e REST endpoints interativamente</p>
              <Link href="/api-explorer" className={styles.featureLink}>
                Explorar →
              </Link>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>📋</div>
              <h3>Gerenciamento de Orders</h3>
              <p>Super-contêineres que organizam todos os documentos de uma operação</p>
              <Link href="/orders" className={styles.featureLink}>
                Gerenciar Orders →
              </Link>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>🗺️</div>
              <h3>Visualizações Inteligentes</h3>
              <p>Grafos, mapas semânticos e busca visual com D3.js</p>
              <Link href="/visualizations" className={styles.featureLink}>
                Visualizar →
              </Link>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>🔍</div>
              <h3>Busca Clássica</h3>
              <p>Busca tradicional de documentos com filtros</p>
              <Link href="/search" className={styles.featureLink}>
                Buscar →
              </Link>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>📎</div>
              <h3>Upload de Documentos</h3>
              <p>Teste processamento de CT-e, PDFs e imagens</p>
              <Link href="/documents" className={styles.featureLink}>
                Upload →
              </Link>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>⚙️</div>
              <h3>Configurações</h3>
              <p>Personalize o sistema e visualize logs</p>
              <Link href="/settings" className={styles.featureLink}>
                Configurar →
              </Link>
            </div>
          </div>
        </div>
      </section>


      {/* Footer */}
      <footer className={styles.footer}>
        <p>MIT Logistics v2.0 • OpenAI + Gemini</p>
      </footer>
      
      {/* Authentication Modal */}
      <AuthModal 
        isOpen={showAuthModal} 
        onClose={() => setShowAuthModal(false)} 
      />
    </div>
  )
}