'use client'

import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

interface SemanticPoint {
  id: string
  x: number
  y: number
  z?: number
  label: string
  category: string
  order_id: string | null
  data: any
}

interface SemanticCluster {
  name: string
  color: string
  documents: string[]
}

interface SemanticMapProps {
  points: SemanticPoint[]
  clusters: SemanticCluster[]
  dimensions: number
  height: number
}

export default function SemanticMap({ points, clusters, dimensions, height }: SemanticMapProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current || points.length === 0) return

    // Limpar conteúdo anterior
    d3.select(containerRef.current).selectAll("*").remove()

    if (dimensions === 3) {
      render3DMap()
    } else {
      render2DMap()
    }
  }, [points, clusters, dimensions, height])

  const render2DMap = () => {
    if (!containerRef.current) return

    const width = containerRef.current.clientWidth
    const margin = { top: 20, right: 20, bottom: 20, left: 20 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const svg = d3.select(containerRef.current)
      .append("svg")
      .attr("width", width)
      .attr("height", height)

    const container = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`)

    // Escalas
    const xExtent = d3.extent(points, d => d.x) as [number, number]
    const yExtent = d3.extent(points, d => d.y) as [number, number]
    
    const xScale = d3.scaleLinear()
      .domain(xExtent)
      .range([0, innerWidth])
    
    const yScale = d3.scaleLinear()
      .domain(yExtent)
      .range([innerHeight, 0]) // Inverter Y para coordenadas SVG

    // Criar mapa de cores dos clusters
    const colorMap = new Map()
    clusters.forEach(cluster => {
      cluster.documents.forEach(docId => {
        colorMap.set(docId, cluster.color)
      })
    })

    // Zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.5, 10])
      .on("zoom", (event) => {
        container.attr("transform", 
          `translate(${margin.left + event.transform.x},${margin.top + event.transform.y}) scale(${event.transform.k})`
        )
      })

    svg.call(zoom as any)

    // Tooltip
    const tooltip = d3.select("body").append("div")
      .attr("class", "semantic-tooltip")
      .style("opacity", 0)
      .style("position", "absolute")
      .style("background", "rgba(0, 0, 0, 0.9)")
      .style("color", "white")
      .style("padding", "10px")
      .style("border-radius", "8px")
      .style("font-size", "12px")
      .style("pointer-events", "none")
      .style("z-index", "1000")
      .style("max-width", "300px")

    // Desenhar pontos
    const dots = container.selectAll(".semantic-dot")
      .data(points)
      .enter()
      .append("circle")
      .attr("class", "semantic-dot")
      .attr("cx", d => xScale(d.x))
      .attr("cy", d => yScale(d.y))
      .attr("r", 6)
      .attr("fill", d => colorMap.get(d.id) || "#6b7280")
      .attr("opacity", 0.7)
      .attr("stroke", "#fff")
      .attr("stroke-width", 1)
      .style("cursor", "pointer")

    // Interações
    dots
      .on("mouseover", function(event, d) {
        // Highlight ponto
        d3.select(this)
          .transition()
          .duration(200)
          .attr("r", 8)
          .attr("opacity", 1)

        // Mostrar tooltip
        tooltip.transition()
          .duration(200)
          .style("opacity", 1)
        
        const content = `
          <strong>${d.label}</strong><br/>
          <strong>Categoria:</strong> ${d.category || 'N/A'}<br/>
          <strong>Coordenadas:</strong> (${d.x.toFixed(2)}, ${d.y.toFixed(2)})<br/>
          ${d.data.extracted_text_preview ? 
            `<strong>Conteúdo:</strong><br/>${d.data.extracted_text_preview}...` : 
            ''
          }
        `
        
        tooltip.html(content)
          .style("left", (event.pageX + 15) + "px")
          .style("top", (event.pageY - 10) + "px")
      })
      .on("mouseout", function() {
        // Reset ponto
        d3.select(this)
          .transition()
          .duration(200)
          .attr("r", 6)
          .attr("opacity", 0.7)

        // Esconder tooltip
        tooltip.transition()
          .duration(500)
          .style("opacity", 0)
      })
      .on("click", function(event, d) {
        // Highlight documentos da mesma categoria
        const sameCategory = points.filter(p => p.category === d.category)
        
        dots.transition()
          .duration(300)
          .attr("opacity", point => 
            sameCategory.includes(point) ? 1 : 0.2
          )
          .attr("r", point => 
            sameCategory.includes(point) ? 8 : 6
          )

        // Reset após 3 segundos
        setTimeout(() => {
          dots.transition()
            .duration(300)
            .attr("opacity", 0.7)
            .attr("r", 6)
        }, 3000)
      })

    // Cleanup function
    return () => {
      tooltip.remove()
    }
  }

  const render3DMap = () => {
    if (!containerRef.current) return

    // Para 3D, vamos usar uma projeção isométrica simples
    const width = containerRef.current.clientWidth
    const margin = { top: 20, right: 20, bottom: 20, left: 20 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const svg = d3.select(containerRef.current)
      .append("svg")
      .attr("width", width)
      .attr("height", height)

    const container = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`)

    // Escalas 3D
    const xExtent = d3.extent(points, d => d.x) as [number, number]
    const yExtent = d3.extent(points, d => d.y) as [number, number]
    const zExtent = d3.extent(points, d => d.z || 0) as [number, number]
    
    const xScale = d3.scaleLinear().domain(xExtent).range([0, innerWidth * 0.8])
    const yScale = d3.scaleLinear().domain(yExtent).range([innerHeight * 0.8, 0])
    const zScale = d3.scaleLinear().domain(zExtent).range([0, 100]) // Profundidade

    // Projeção isométrica simples
    const project = (x: number, y: number, z: number) => ({
      x: x + z * 0.3,
      y: y - z * 0.3
    })

    // Criar mapa de cores
    const colorMap = new Map()
    clusters.forEach(cluster => {
      cluster.documents.forEach(docId => {
        colorMap.set(docId, cluster.color)
      })
    })

    // Ordenar pontos por profundidade (z) para renderização correta
    const sortedPoints = [...points].sort((a, b) => (a.z || 0) - (b.z || 0))

    // Tooltip
    const tooltip = d3.select("body").append("div")
      .attr("class", "semantic-tooltip-3d")
      .style("opacity", 0)
      .style("position", "absolute")
      .style("background", "rgba(0, 0, 0, 0.9)")
      .style("color", "white")
      .style("padding", "10px")
      .style("border-radius", "8px")
      .style("font-size", "12px")
      .style("pointer-events", "none")
      .style("z-index", "1000")
      .style("max-width", "300px")

    // Desenhar pontos 3D
    const dots = container.selectAll(".semantic-dot-3d")
      .data(sortedPoints)
      .enter()
      .append("circle")
      .attr("class", "semantic-dot-3d")
      .attr("cx", d => {
        const scaled = { x: xScale(d.x), y: yScale(d.y), z: zScale(d.z || 0) }
        return project(scaled.x, scaled.y, scaled.z).x
      })
      .attr("cy", d => {
        const scaled = { x: xScale(d.x), y: yScale(d.y), z: zScale(d.z || 0) }
        return project(scaled.x, scaled.y, scaled.z).y
      })
      .attr("r", d => 4 + (d.z || 0) * 2) // Tamanho baseado em profundidade
      .attr("fill", d => colorMap.get(d.id) || "#6b7280")
      .attr("opacity", d => 0.6 + ((d.z || 0) - zExtent[0]) / (zExtent[1] - zExtent[0]) * 0.4)
      .attr("stroke", "#fff")
      .attr("stroke-width", 1)
      .style("cursor", "pointer")

    // Interações 3D
    dots
      .on("mouseover", function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr("r", (4 + (d.z || 0) * 2) * 1.5)
          .attr("opacity", 1)

        tooltip.transition()
          .duration(200)
          .style("opacity", 1)
        
        const content = `
          <strong>${d.label}</strong><br/>
          <strong>Categoria:</strong> ${d.category || 'N/A'}<br/>
          <strong>Coordenadas 3D:</strong> (${d.x.toFixed(2)}, ${d.y.toFixed(2)}, ${(d.z || 0).toFixed(2)})<br/>
          ${d.data.extracted_text_preview ? 
            `<strong>Conteúdo:</strong><br/>${d.data.extracted_text_preview}...` : 
            ''
          }
        `
        
        tooltip.html(content)
          .style("left", (event.pageX + 15) + "px")
          .style("top", (event.pageY - 10) + "px")
      })
      .on("mouseout", function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr("r", 4 + (d.z || 0) * 2)
          .attr("opacity", 0.6 + ((d.z || 0) - zExtent[0]) / (zExtent[1] - zExtent[0]) * 0.4)

        tooltip.transition()
          .duration(500)
          .style("opacity", 0)
      })

    // Cleanup
    return () => {
      tooltip.remove()
    }
  }

  return (
    <div ref={containerRef} className="w-full h-full bg-gray-50 rounded" />
  )
}