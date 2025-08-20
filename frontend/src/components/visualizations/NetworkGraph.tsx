'use client'

import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { gatekeeperClient } from '@/lib/api/client'

interface GraphNode {
  id: string
  type: 'order' | 'document'
  label: string
  data: any
}

interface GraphEdge {
  source: string
  target: string
  type: string
}

interface NetworkGraphProps {
  nodes: GraphNode[]
  edges: GraphEdge[]
  height: number
}

interface ContextMenuState {
  visible: boolean
  x: number
  y: number
  node: GraphNode | null
}

export default function NetworkGraph({ nodes, edges, height }: NetworkGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [contextMenu, setContextMenu] = useState<ContextMenuState>({
    visible: false,
    x: 0,
    y: 0,
    node: null
  })
  const [loading, setLoading] = useState(false)

  // Função para lidar com clique nos nós
  const handleNodeClick = (event: MouseEvent, node: GraphNode) => {
    event.preventDefault()
    setContextMenu({
      visible: true,
      x: event.clientX,
      y: event.clientY,
      node
    })
  }

  // Fechar menu contextual
  const closeContextMenu = () => {
    setContextMenu(prev => ({ ...prev, visible: false }))
  }

  // Visualizar metadados JSON
  const viewMetadata = async (node: GraphNode) => {
    if (node.type !== 'document') return
    
    try {
      setLoading(true)
      const documentId = node.data.id || node.data.file_id
      const metadata = await gatekeeperClient.getRaw(`/files/${documentId}/metadata`)
      
      // Abrir em nova aba com JSON formatado
      const newWindow = window.open()
      if (newWindow) {
        newWindow.document.write(`
          <html>
            <head>
              <title>Metadados - ${node.label}</title>
              <style>
                body { font-family: 'Monaco', 'Consolas', monospace; margin: 20px; background: #f5f5f5; }
                .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
                .title { color: #333; margin: 0; }
                .subtitle { color: #666; margin: 5px 0 0 0; }
                pre { background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto; border: 1px solid #e9ecef; }
                .actions { margin-top: 15px; }
                .btn { background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; margin-right: 10px; cursor: pointer; }
                .btn:hover { background: #0056b3; }
              </style>
            </head>
            <body>
              <div class="container">
                <div class="header">
                  <h1 class="title">📄 ${node.label}</h1>
                  <p class="subtitle">Metadados completos do documento</p>
                </div>
                <pre>${JSON.stringify(metadata, null, 2)}</pre>
                <div class="actions">
                  <button class="btn" onclick="navigator.clipboard.writeText('${JSON.stringify(metadata)}')">
                    📋 Copiar JSON
                  </button>
                  <button class="btn" onclick="window.close()">
                    ✖️ Fechar
                  </button>
                </div>
              </div>
            </body>
          </html>
        `)
      }
    } catch (error) {
      console.error('Erro ao buscar metadados:', error)
      alert('Erro ao carregar metadados do documento')
    } finally {
      setLoading(false)
      closeContextMenu()
    }
  }

  // Baixar documento
  const downloadDocument = async (node: GraphNode) => {
    if (node.type !== 'document') return
    
    try {
      setLoading(true)
      const documentId = node.data.id || node.data.file_id
      const downloadInfo = await gatekeeperClient.getRaw(`/files/${documentId}/download`)
      
      // Criar link temporário para download
      const link = document.createElement('a')
      link.href = downloadInfo.download_url
      link.download = downloadInfo.filename
      link.style.display = 'none'
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      // Mostrar confirmação
      alert(`Download iniciado: ${downloadInfo.filename}\nExpira em: ${new Date(downloadInfo.expires_at).toLocaleString()}`)
      
    } catch (error) {
      console.error('Erro ao baixar documento:', error)
      alert('Erro ao gerar link de download. O documento pode não estar disponível no S3.')
    } finally {
      setLoading(false)
      closeContextMenu()
    }
  }

  // Visualizar ordem
  const viewOrder = async (node: GraphNode) => {
    if (node.type !== 'order') return
    
    try {
      const orderData = {
        order: node.data,
        documents_count: node.data.total_documents || 0,
        type: 'Super-contêiner logístico'
      }
      
      const newWindow = window.open()
      if (newWindow) {
        newWindow.document.write(`
          <html>
            <head>
              <title>Order Details - ${node.label}</title>
              <style>
                body { font-family: system-ui, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 800px; }
                .header { margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
                .title { color: #333; margin: 0; }
                .subtitle { color: #666; margin: 5px 0 0 0; }
                .section { margin: 15px 0; }
                .label { font-weight: bold; color: #555; }
                .value { margin-left: 10px; }
                .status { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
                .status-created { background: #d4edda; color: #155724; }
                .status-processing { background: #fff3cd; color: #856404; }
                .status-completed { background: #cce5ff; color: #004085; }
                pre { background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto; border: 1px solid #e9ecef; }
              </style>
            </head>
            <body>
              <div class="container">
                <div class="header">
                  <h1 class="title">📋 ${node.label}</h1>
                  <p class="subtitle">Detalhes da Order (Super-contêiner)</p>
                </div>
                
                <div class="section">
                  <span class="label">ID:</span>
                  <span class="value">${node.data.id || 'N/A'}</span>
                </div>
                
                <div class="section">
                  <span class="label">Order ID:</span>
                  <span class="value">${node.data.order_id || 'N/A'}</span>
                </div>
                
                <div class="section">
                  <span class="label">Cliente:</span>
                  <span class="value">${node.data.customer || node.data.customer_name || 'N/A'}</span>
                </div>
                
                <div class="section">
                  <span class="label">Status:</span>
                  <span class="value status status-${node.data.status || 'created'}">${node.data.status || 'created'}</span>
                </div>
                
                <div class="section">
                  <span class="label">Documentos:</span>
                  <span class="value">${node.data.total_documents || 0} arquivo(s)</span>
                </div>
                
                <div class="section">
                  <span class="label">Criado em:</span>
                  <span class="value">${node.data.created_at ? new Date(node.data.created_at).toLocaleString() : 'N/A'}</span>
                </div>
                
                <h3>Dados Completos (JSON):</h3>
                <pre>${JSON.stringify(orderData, null, 2)}</pre>
              </div>
            </body>
          </html>
        `)
      }
    } catch (error) {
      console.error('Erro ao visualizar order:', error)
      alert('Erro ao carregar dados da order')
    } finally {
      closeContextMenu()
    }
  }

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove() // Limpar conteúdo anterior

    const width = svgRef.current.clientWidth
    const margin = 20

    // Configurar simulação de força
    const simulation = d3.forceSimulation(nodes as any)
      .force("link", d3.forceLink(edges).id((d: any) => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))

    // Criar container principal
    const container = svg.append("g")

    // Zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.5, 3])
      .on("zoom", (event) => {
        container.attr("transform", event.transform)
      })

    svg.call(zoom as any)
    
    // Click no SVG para fechar menu contextual
    svg.on("click", () => {
      console.log('SVG clicado - fechando menu contextual')
      closeContextMenu()
    })

    // Criar links (arestas)
    const link = container.selectAll(".link")
      .data(edges)
      .enter()
      .append("line")
      .attr("class", "link")
      .attr("stroke", "#999")
      .attr("stroke-width", 2)
      .attr("stroke-opacity", 0.6)

    // Criar nodes (nós)
    const node = container.selectAll(".node")
      .data(nodes)
      .enter()
      .append("g")
      .attr("class", "node")
      .call(d3.drag()
        .on("start", (event, d: any) => {
          if (!event.active) simulation.alphaTarget(0.3).restart()
          d.fx = d.x
          d.fy = d.y
        })
        .on("drag", (event, d: any) => {
          d.fx = event.x
          d.fy = event.y
        })
        .on("end", (event, d: any) => {
          if (!event.active) simulation.alphaTarget(0)
          d.fx = null
          d.fy = null
        }) as any)

    // Círculos dos nodes
    node.append("circle")
      .attr("r", (d: any) => d.type === 'order' ? 20 : 15)
      .attr("fill", (d: any) => d.type === 'order' ? "#3b82f6" : "#10b981")
      .attr("stroke", "#fff")
      .attr("stroke-width", 2)

    // Ícones nos nodes
    node.append("text")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("fill", "white")
      .attr("font-size", (d: any) => d.type === 'order' ? "16px" : "12px")
      .attr("font-weight", "bold")
      .text((d: any) => d.type === 'order' ? "📋" : "📄")

    // Adicionar evento de clique nos nós
    node.on("click", (event: MouseEvent, d: any) => {
      event.preventDefault()
      event.stopPropagation()
      console.log('Nó clicado:', d.label, d.type)
      handleNodeClick(event, d)
    })

    // Adicionar visual de hover
    node.style("cursor", "pointer")
      .on("mouseenter", function() {
        d3.select(this).select("circle")
          .transition()
          .duration(200)
          .attr("r", (d: any) => (d.type === 'order' ? 20 : 15) * 1.1)
          .attr("stroke-width", 3)
      })
      .on("mouseleave", function() {
        d3.select(this).select("circle")
          .transition()
          .duration(200)
          .attr("r", (d: any) => d.type === 'order' ? 20 : 15)
          .attr("stroke-width", 2)
      })

    // Labels dos nodes
    node.append("text")
      .attr("text-anchor", "middle")
      .attr("dy", (d: any) => d.type === 'order' ? 35 : 30)
      .attr("font-size", "12px")
      .attr("fill", "#374151")
      .text((d: any) => {
        const maxLength = 20
        return d.label.length > maxLength 
          ? d.label.substring(0, maxLength) + "..." 
          : d.label
      })

    // Tooltip
    const tooltip = d3.select("body").append("div")
      .attr("class", "tooltip")
      .style("opacity", 0)
      .style("position", "absolute")
      .style("background", "rgba(0, 0, 0, 0.8)")
      .style("color", "white")
      .style("padding", "8px")
      .style("border-radius", "4px")
      .style("font-size", "12px")
      .style("pointer-events", "none")
      .style("z-index", "1000")

    node
      .on("mouseover", function(event, d: any) {
        tooltip.transition()
          .duration(200)
          .style("opacity", .9)
        
        const content = d.type === 'order' 
          ? `<strong>Order:</strong> ${d.label}<br/>
             <strong>Cliente:</strong> ${d.data.customer || 'N/A'}<br/>
             <strong>Status:</strong> ${d.data.status || 'N/A'}<br/>
             <strong>Documentos:</strong> ${d.data.total_documents || 0}`
          : `<strong>Documento:</strong> ${d.label}<br/>
             <strong>Tipo:</strong> ${d.data.file_type || 'N/A'}<br/>
             <strong>Categoria:</strong> ${d.data.category || 'N/A'}<br/>
             <strong>Status:</strong> ${d.data.processing_status || 'N/A'}`
        
        tooltip.html(content)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 10) + "px")
      })
      .on("mouseout", function() {
        tooltip.transition()
          .duration(500)
          .style("opacity", 0)
      })

    // Atualizar posições na simulação
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y)

      node
        .attr("transform", (d: any) => `translate(${d.x},${d.y})`)
    })

    // Cleanup
    return () => {
      tooltip.remove()
      simulation.stop()
    }

  }, [nodes, edges, height])

  const handleZoomIn = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current)
      svg.transition().duration(300).call(
        d3.zoom().scaleBy as any, 1.5
      )
    }
  }

  const handleZoomOut = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current)
      svg.transition().duration(300).call(
        d3.zoom().scaleBy as any, 1/1.5
      )
    }
  }

  const handleReset = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current)
      svg.transition().duration(500).call(
        d3.zoom().transform as any, d3.zoomIdentity
      )
    }
  }

  return (
    <div className="relative w-full h-full">
      {/* Zoom Controls */}
      <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
        <button
          onClick={handleZoomIn}
          className="w-8 h-8 bg-white shadow-md rounded border hover:bg-gray-50 flex items-center justify-center text-sm font-bold"
          title="Zoom In"
        >
          +
        </button>
        <button
          onClick={handleZoomOut}
          className="w-8 h-8 bg-white shadow-md rounded border hover:bg-gray-50 flex items-center justify-center text-sm font-bold"
          title="Zoom Out"
        >
          −
        </button>
        <button
          onClick={handleReset}
          className="w-8 h-8 bg-white shadow-md rounded border hover:bg-gray-50 flex items-center justify-center text-xs"
          title="Reset Zoom"
        >
          ⌂
        </button>
      </div>
      
      {/* Help Text */}
      <div className="absolute bottom-4 left-4 text-xs text-gray-500 bg-white bg-opacity-90 px-2 py-1 rounded">
        Arraste para mover • Roda do mouse para zoom • Clique nos nós para ações • Arraste nodes para reposicionar
      </div>

      {/* Context Menu */}
      {console.log('Context Menu State:', contextMenu)}
      {contextMenu.visible && contextMenu.node && (
        <div 
          className="absolute bg-white rounded-lg shadow-lg border border-gray-200 py-2 min-w-48"
          style={{ 
            left: contextMenu.x, 
            top: contextMenu.y,
            transform: 'translate(-50%, -10px)',
            zIndex: 9999,
            position: 'fixed'
          }}
        >
          <div className="px-3 py-2 border-b border-gray-100">
            <div className="font-semibold text-gray-900 text-sm">
              {contextMenu.node.type === 'order' ? '📋' : '📄'} {contextMenu.node.label}
            </div>
            <div className="text-xs text-gray-500">
              {contextMenu.node.type === 'order' ? 'Super-contêiner' : 'Documento'}
            </div>
          </div>
          
          {contextMenu.node.type === 'document' && (
            <>
              <button
                onClick={() => viewMetadata(contextMenu.node!)}
                disabled={loading}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2 disabled:opacity-50"
              >
                📄 Ver Metadados (JSON)
              </button>
              <button
                onClick={() => downloadDocument(contextMenu.node!)}
                disabled={loading}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2 disabled:opacity-50"
              >
                💾 Baixar Documento
              </button>
            </>
          )}
          
          {contextMenu.node.type === 'order' && (
            <button
              onClick={() => viewOrder(contextMenu.node!)}
              disabled={loading}
              className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2 disabled:opacity-50"
            >
              📋 Ver Detalhes da Order
            </button>
          )}
          
          <div className="border-t border-gray-100 mt-1">
            <button
              onClick={closeContextMenu}
              className="w-full px-3 py-2 text-left text-sm text-gray-500 hover:bg-gray-50"
            >
              ✖️ Fechar
            </button>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center z-30">
          <div className="bg-white rounded-lg p-4 shadow-lg">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <div className="mt-2 text-sm text-gray-600">Carregando...</div>
          </div>
        </div>
      )}

      <svg
        ref={svgRef}
        width="100%"
        height={height}
        className="border-none"
      />
    </div>
  )
}