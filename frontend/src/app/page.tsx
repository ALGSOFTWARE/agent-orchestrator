// 🏠 MIT Logistics Frontend - Homepage

import { Metadata } from 'next'
import Link from 'next/link'
import styles from '@/styles/modules/HomePage.module.css'

export const metadata: Metadata = {
  title: 'MIT Logistics - Dashboard',
  description: 'Transformando logística em inteligência real - Sistema de testes para agentes de IA',
}

export default function HomePage() {
  return (
    <div className={styles.container}>
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
            Dashboard interativo para teste e validação de agentes de IA especializados 
            em operações logísticas, monitoramento de containers e processamento de CT-e.
          </p>

          <div className={styles.actions}>
            <Link href="/agents" className={styles.primaryButton}>
              🤖 Testar Agentes
            </Link>
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
              <h3>Logistics Agent</h3>
              <p>CT-e, containers e rastreamento</p>
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
              <Link href="/agents/playground" className={styles.featureLink}>
                Experimentar →
              </Link>
            </div>

            <div className={styles.feature}>
              <div className={styles.featureIcon}>💬</div>
              <h3>Chat Interativo</h3>
              <p>Converse diretamente com agentes especializados</p>
              <Link href="/agents" className={styles.featureLink}>
                Conversar →
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
              <div className={styles.featureIcon}>📎</div>
              <h3>Upload de Documentos</h3>
              <p>Teste processamento de CT-e, PDFs e imagens</p>
              <Link href="/agents?tab=upload" className={styles.featureLink}>
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

      {/* Status Section */}
      <section className={styles.status}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Status do Sistema</h2>
          
          <div className={styles.statusGrid}>
            <div className={styles.statusItem}>
              <div className={styles.statusIndicator} data-status="loading">
                <div className={styles.pulse}></div>
              </div>
              <div className={styles.statusInfo}>
                <h4>GraphQL API</h4>
                <p>Verificando conexão...</p>
              </div>
            </div>

            <div className={styles.statusItem}>
              <div className={styles.statusIndicator} data-status="loading">
                <div className={styles.pulse}></div>
              </div>
              <div className={styles.statusInfo}>
                <h4>Gatekeeper Agent</h4>
                <p>Verificando conexão...</p>
              </div>
            </div>

            <div className={styles.statusItem}>
              <div className={styles.statusIndicator} data-status="loading">
                <div className={styles.pulse}></div>
              </div>
              <div className={styles.statusInfo}>
                <h4>Ollama LLM</h4>
                <p>Verificando conexão...</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className={styles.container}>
          <p>
            MIT Logistics Dashboard v1.0.0 - 
            Sistema de testes para agentes de IA especializados
          </p>
          <div className={styles.footerLinks}>
            <Link href="/api-explorer/graphql">GraphQL Playground</Link>
            <span>•</span>
            <Link href="/monitoring/logs">Logs do Sistema</Link>
            <span>•</span>
            <Link href="/settings">Configurações</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}