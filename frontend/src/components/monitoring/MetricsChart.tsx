// 📊 MIT Logistics Frontend - Metrics Chart Component

'use client'

import { useEffect, useRef } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui'
import type { SystemMetrics } from '@/types'
import styles from '@/styles/modules/MetricsChart.module.css'

interface MetricsChartProps {
  metrics: SystemMetrics[]
  title: string
  type: 'cpu' | 'memory' | 'disk' | 'network'
}

export function MetricsChart({ metrics, title, type }: MetricsChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const getDataPoints = (metrics: SystemMetrics[]) => {
    switch (type) {
      case 'cpu':
        return metrics.map(m => m.cpu_usage)
      case 'memory':
        return metrics.map(m => m.memory_usage)
      case 'disk':
        return metrics.map(m => m.disk_usage)
      case 'network':
        return metrics.map(m => m.network_io.bytes_sent + m.network_io.bytes_received)
      default:
        return []
    }
  }

  const formatValue = (value: number) => {
    switch (type) {
      case 'cpu':
      case 'memory':
      case 'disk':
        return `${value.toFixed(1)}%`
      case 'network':
        return formatBytes(value)
      default:
        return value.toString()
    }
  }

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`
  }

  const getThresholdColor = (value: number) => {
    switch (type) {
      case 'cpu':
      case 'memory':
      case 'disk':
        if (value > 80) return 'var(--color-error)'
        if (value > 60) return 'var(--color-warning)'
        return 'var(--color-success)'
      default:
        return 'var(--color-primary-600)'
    }
  }

  const drawChart = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const rect = canvas.getBoundingClientRect()
    const dpr = window.devicePixelRatio || 1
    
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    
    ctx.scale(dpr, dpr)
    
    const width = rect.width
    const height = rect.height
    const padding = 20

    // Clear canvas
    ctx.clearRect(0, 0, width, height)

    if (metrics.length === 0) {
      ctx.fillStyle = 'var(--color-muted-foreground)'
      ctx.font = '14px Inter'
      ctx.textAlign = 'center'
      ctx.fillText('Sem dados disponíveis', width / 2, height / 2)
      return
    }

    const dataPoints = getDataPoints(metrics)
    const maxValue = Math.max(...dataPoints, type === 'network' ? 1024 : 100)
    const minValue = Math.min(...dataPoints, 0)

    // Draw grid lines
    ctx.strokeStyle = 'var(--color-border)'
    ctx.lineWidth = 1
    
    const gridLines = 5
    for (let i = 0; i <= gridLines; i++) {
      const y = padding + (height - 2 * padding) * (i / gridLines)
      ctx.beginPath()
      ctx.moveTo(padding, y)
      ctx.lineTo(width - padding, y)
      ctx.stroke()
    }

    // Draw chart line
    ctx.strokeStyle = getThresholdColor(dataPoints[dataPoints.length - 1] || 0)
    ctx.lineWidth = 2
    ctx.beginPath()

    const pointWidth = (width - 2 * padding) / Math.max(dataPoints.length - 1, 1)

    dataPoints.forEach((value, index) => {
      const x = padding + index * pointWidth
      const y = height - padding - ((value - minValue) / (maxValue - minValue)) * (height - 2 * padding)
      
      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })

    ctx.stroke()

    // Draw fill area
    ctx.globalAlpha = 0.1
    ctx.fillStyle = getThresholdColor(dataPoints[dataPoints.length - 1] || 0)
    ctx.lineTo(width - padding, height - padding)
    ctx.lineTo(padding, height - padding)
    ctx.closePath()
    ctx.fill()
    ctx.globalAlpha = 1

    // Draw data points
    ctx.fillStyle = getThresholdColor(dataPoints[dataPoints.length - 1] || 0)
    dataPoints.forEach((value, index) => {
      const x = padding + index * pointWidth
      const y = height - padding - ((value - minValue) / (maxValue - minValue)) * (height - 2 * padding)
      
      ctx.beginPath()
      ctx.arc(x, y, 3, 0, 2 * Math.PI)
      ctx.fill()
    })
  }

  useEffect(() => {
    drawChart()
  }, [metrics, type])

  useEffect(() => {
    const handleResize = () => drawChart()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const dataPoints = getDataPoints(metrics)
  const currentValue = dataPoints.length > 0 ? (dataPoints[dataPoints.length - 1] ?? 0) : 0
  const previousValue = dataPoints.length > 1 ? (dataPoints[dataPoints.length - 2] ?? 0) : currentValue
  const trend = currentValue - previousValue

  return (
    <Card className={styles.card}>
      <CardHeader>
        <div className={styles.header}>
          <CardTitle level={4}>{title}</CardTitle>
          <div className={styles.currentValue}>
            <span className={styles.value}>
              {formatValue(currentValue)}
            </span>
            {trend !== 0 && (
              <span className={`${styles.trend} ${trend > 0 ? styles.up : styles.down}`}>
                {trend > 0 ? '↗' : '↘'} {Math.abs(trend).toFixed(1)}
              </span>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className={styles.chartContainer}>
          <canvas 
            ref={canvasRef}
            className={styles.canvas}
            width={400}
            height={200}
          />
          
          {metrics.length > 0 && (
            <div className={styles.chartInfo}>
              <div className={styles.timeRange}>
                Últimos {metrics.length} pontos
              </div>
              <div className={styles.lastUpdate}>
                Atualizado: {new Date(metrics[metrics.length - 1]?.timestamp || Date.now()).toLocaleTimeString('pt-BR')}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}