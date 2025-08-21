'use client'

import Link from 'next/link'
import { Settings, Brain, Database, Shield, Monitor, Cog } from 'lucide-react'
import styles from './settings.module.css'

export default function SettingsPage() {
  const settingCategories = [
    {
      title: 'LLM Configuration',
      description: 'Configurar modelos de linguagem e roteamento inteligente',
      icon: Brain,
      href: '/settings/llm',
      color: 'purple'
    },
    {
      title: 'Database Settings',
      description: 'Configurações do MongoDB e índices de busca vetorial',
      icon: Database,
      href: '/settings/database',
      color: 'green'
    },
    {
      title: 'Authentication',
      description: 'Gerenciar usuários, roles e permissões',
      icon: Shield,
      href: '/settings/auth',
      color: 'blue'
    },
    {
      title: 'System Monitoring',
      description: 'Logs, métricas e alertas do sistema',
      icon: Monitor,
      href: '/settings/monitoring',
      color: 'orange'
    },
    {
      title: 'General Settings',
      description: 'Configurações gerais do sistema MIT Logistics',
      icon: Cog,
      href: '/settings/general',
      color: 'gray'
    }
  ]

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>⚙️ Configurações</h1>
          <p className={styles.description}>
            Gerencie as configurações do sistema MIT Logistics
          </p>
        </div>
      </div>

      <div className={styles.content}>
        <div className={styles.grid}>
          {settingCategories.map((category) => {
            const IconComponent = category.icon
            return (
              <Link 
                key={category.href} 
                href={category.href}
                className={`${styles.card} ${styles[`card-${category.color}`]}`}
              >
                <div className={styles.cardHeader}>
                  <div className={styles.cardIcon}>
                    <IconComponent className={styles.icon} />
                  </div>
                  <div className={styles.cardTitle}>
                    <h3>{category.title}</h3>
                  </div>
                </div>
                <div className={styles.cardDescription}>
                  <p>{category.description}</p>
                </div>
                <div className={styles.cardArrow}>
                  →
                </div>
              </Link>
            )
          })}
        </div>

        <div className={styles.systemInfo}>
          <div className={styles.infoCard}>
            <h4>Sistema Ativo</h4>
            <div className={styles.infoGrid}>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Versão:</span>
                <span className={styles.infoValue}>v2.0.0</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>LLM Providers:</span>
                <span className={styles.infoValue}>OpenAI + Gemini</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Database:</span>
                <span className={styles.infoValue}>MongoDB Atlas</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>Status:</span>
                <span className={styles.infoValue}>🟢 Online</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}