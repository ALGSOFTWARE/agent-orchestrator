'use client'

import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { gatekeeperClient } from '@/lib/api/client'

interface GraphNode {
  id: string
  type: 'order' | 'document'
  label: string
  data: any
  highlighted?: boolean
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
      
      // Criar uma janela modal mais robusta
      const newWindow = window.open('', '_blank', 'width=1000,height=700,scrollbars=yes,resizable=yes')
      if (newWindow) {
        newWindow.document.write(`
          <!DOCTYPE html>
          <html lang="pt-BR">
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>Metadados - ${node.label}</title>
              <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                  font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  min-height: 100vh;
                  padding: 20px;
                }
                .container { 
                  background: white; 
                  padding: 30px; 
                  border-radius: 16px; 
                  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                  max-width: 900px;
                  margin: 0 auto;
                }
                .header { 
                  margin-bottom: 30px; 
                  border-bottom: 2px solid #e5e7eb; 
                  padding-bottom: 20px;
                  text-align: center;
                }
                .title { 
                  color: #1f2937; 
                  font-size: 28px;
                  font-weight: 700;
                  margin-bottom: 8px;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  gap: 12px;
                }
                .subtitle { 
                  color: #6b7280; 
                  font-size: 16px;
                  font-weight: 500;
                }
                .json-container {
                  background: #f8fafc;
                  border: 2px solid #e2e8f0;
                  border-radius: 12px;
                  padding: 0;
                  margin: 20px 0;
                  overflow: hidden;
                }
                .json-header {
                  background: #1e293b;
                  color: white;
                  padding: 12px 20px;
                  font-weight: 600;
                  font-size: 14px;
                  display: flex;
                  justify-content: between;
                  align-items: center;
                }
                pre { 
                  background: transparent;
                  padding: 20px; 
                  overflow-x: auto; 
                  font-family: 'JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', monospace;
                  font-size: 13px;
                  line-height: 1.5;
                  color: #1e293b;
                  max-height: 400px;
                  overflow-y: auto;
                }
                .actions { 
                  margin-top: 25px;
                  display: flex;
                  gap: 12px;
                  justify-content: center;
                  flex-wrap: wrap;
                }
                .btn { 
                  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  color: white; 
                  border: none; 
                  padding: 12px 24px; 
                  border-radius: 8px; 
                  cursor: pointer; 
                  font-weight: 600;
                  font-size: 14px;
                  transition: all 0.2s ease;
                  display: flex;
                  align-items: center;
                  gap: 8px;
                }
                .btn:hover { 
                  transform: translateY(-2px);
                  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
                }
                .btn.secondary {
                  background: #6b7280;
                }
                .btn.secondary:hover {
                  background: #4b5563;
                  box-shadow: 0 10px 20px rgba(107, 114, 128, 0.4);
                }
                .stats {
                  display: grid;
                  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                  gap: 15px;
                  margin: 20px 0;
                }
                .stat-card {
                  background: #f1f5f9;
                  padding: 15px;
                  border-radius: 8px;
                  text-align: center;
                  border: 1px solid #e2e8f0;
                }
                .stat-label {
                  font-size: 12px;
                  color: #64748b;
                  font-weight: 600;
                  text-transform: uppercase;
                  letter-spacing: 0.5px;
                }
                .stat-value {
                  font-size: 18px;
                  color: #1e293b;
                  font-weight: 700;
                  margin-top: 4px;
                }
              </style>
            </head>
            <body>
              <div class="container">
                <div class="header">
                  <h1 class="title">
                    <span>📄</span>
                    <span>${node.label}</span>
                  </h1>
                  <p class="subtitle">Metadados completos do documento digital</p>
                </div>
                
                <div class="stats">
                  <div class="stat-card">
                    <div class="stat-label">Tipo</div>
                    <div class="stat-value">${metadata?.document?.file_type || 'N/A'}</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-label">Tamanho</div>
                    <div class="stat-value">${metadata?.document?.size_bytes ? Math.round(metadata.document.size_bytes / 1024) + ' KB' : 'N/A'}</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-label">Status</div>
                    <div class="stat-value">${metadata?.document?.processing_status || 'N/A'}</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-label">Embedding</div>
                    <div class="stat-value">${metadata?.document?.has_embedding ? '✅ Sim' : '❌ Não'}</div>
                  </div>
                </div>
                
                <div class="json-container">
                  <div class="json-header">
                    📊 Dados JSON Completos
                  </div>
                  <pre id="json-content">${JSON.stringify(metadata, null, 2)}</pre>
                </div>
                
                <div class="actions">
                  <button class="btn" onclick="copyToClipboard()">
                    <span>📋</span>
                    <span>Copiar JSON</span>
                  </button>
                  <button class="btn" onclick="downloadJson()">
                    <span>💾</span>
                    <span>Download JSON</span>
                  </button>
                  <button class="btn secondary" onclick="window.close()">
                    <span>✖️</span>
                    <span>Fechar</span>
                  </button>
                </div>
              </div>
              
              <script>
                function copyToClipboard() {
                  const jsonText = document.getElementById('json-content').textContent;
                  navigator.clipboard.writeText(jsonText).then(() => {
                    const btn = event.target.closest('.btn');
                    const originalText = btn.innerHTML;
                    btn.innerHTML = '<span>✅</span><span>Copiado!</span>';
                    setTimeout(() => {
                      btn.innerHTML = originalText;
                    }, 2000);
                  }).catch(err => {
                    alert('Erro ao copiar: ' + err);
                  });
                }
                
                function downloadJson() {
                  const jsonText = document.getElementById('json-content').textContent;
                  const blob = new Blob([jsonText], { type: 'application/json' });
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = '${node.label.replace(/[^a-zA-Z0-9]/g, '_')}_metadata.json';
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  window.URL.revokeObjectURL(url);
                }
              </script>
            </body>
          </html>
        `)
        newWindow.document.close()
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

    // Aguardar renderização e garantir que temos dimensões válidas
    const initializeGraph = () => {
      const svgElement = svgRef.current
      if (!svgElement) return
      
      const rect = svgElement.getBoundingClientRect()
      const width = rect.width || svgElement.clientWidth || 800
      const actualHeight = rect.height || svgElement.clientHeight || height || 600
      
      console.log(`📊 NetworkGraph dimensions: width=${width}, height=${actualHeight}`)
      
      if (width <= 0 || actualHeight <= 0) {
        console.log(`⏳ NetworkGraph waiting for valid dimensions...`)
        // Aguardar mais um frame se ainda não temos dimensões
        setTimeout(initializeGraph, 100)
        return
      }
      
      console.log(`✅ NetworkGraph initializing with valid dimensions`)
      
      try {

      const svg = d3.select(svgElement)
      svg.selectAll("*").remove() // Limpar conteúdo anterior

      // Calcular parâmetros dinâmicos baseado na quantidade de nós
      const orderNodes = nodes.filter(n => n.type === 'order')
      const docNodes = nodes.filter(n => n.type === 'document')
      
      // Ajustar força de repulsão baseado na densidade
      const nodeCount = nodes.length
      const density = nodeCount / (width * actualHeight / 10000) // densidade por 100x100px
      const repulsionStrength = Math.max(-800, Math.min(-100, -300 * Math.sqrt(density)))
      
      // Distância entre links baseada no número de conexões
      const linkDistance = Math.max(80, Math.min(200, 150 - nodeCount * 0.5))
      
      console.log(`📊 Auto-layout: ${nodeCount} nós, densidade: ${density.toFixed(2)}, repulsão: ${repulsionStrength}, distância: ${linkDistance}`)

      // Posicionamento inicial inteligente dos nós
      const ordersCount = orderNodes.length
      if (ordersCount > 0) {
        // Distribuir orders em círculo ou grid
        if (ordersCount <= 8) {
          // Círculo para poucas orders
          const radius = Math.min(width, actualHeight) * 0.3
          orderNodes.forEach((node: any, i: number) => {
            const angle = (2 * Math.PI * i) / ordersCount
            node.x = width / 2 + radius * Math.cos(angle)
            node.y = actualHeight / 2 + radius * Math.sin(angle)
            node.fx = node.x // Fixar posição inicial
            node.fy = node.y
          })
        } else {
          // Grid para muitas orders
          const cols = Math.ceil(Math.sqrt(ordersCount))
          const rows = Math.ceil(ordersCount / cols)
          const cellWidth = width * 0.8 / cols
          const cellHeight = actualHeight * 0.8 / rows
          const startX = width * 0.1
          const startY = actualHeight * 0.1
          
          orderNodes.forEach((node: any, i: number) => {
            const row = Math.floor(i / cols)
            const col = i % cols
            node.x = startX + col * cellWidth + cellWidth / 2
            node.y = startY + row * cellHeight + cellHeight / 2
            node.fx = node.x
            node.fy = node.y
          })
        }
        
        // Liberar posições fixas após um tempo para permitir ajustes
        setTimeout(() => {
          orderNodes.forEach((node: any) => {
            node.fx = null
            node.fy = null
          })
        }, 1000)
      }

      // Configurar simulação de força com parâmetros dinâmicos
      const simulation = d3.forceSimulation(nodes as any)
        .force("link", d3.forceLink(edges).id((d: any) => d.id).distance(linkDistance))
        .force("charge", d3.forceManyBody().strength(repulsionStrength))
        .force("center", d3.forceCenter(width / 2, actualHeight / 2))
        .force("collision", d3.forceCollide().radius((d: any) => d.type === 'order' ? 35 : 25))
        .force("x", d3.forceX(width / 2).strength(0.05))
        .force("y", d3.forceY(actualHeight / 2).strength(0.05))

      // Criar container principal
      const container = svg.append("g")

      // Zoom behavior com verificação de extensão válida
      const zoom = d3.zoom()
        .scaleExtent([0.1, 5])
        .on("zoom", (event) => {
          container.attr("transform", event.transform)
        })

      // Aplicar zoom apenas quando o SVG tem dimensões
      if (width > 0 && actualHeight > 0) {
        svg.call(zoom as any)
      }
      
      // Click no SVG para fechar menu contextual
      svg.on("click", () => {
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
        .attr("fill", (d: any) => {
          if (d.highlighted) {
            return d.type === 'order' ? "#f59e0b" : "#ef4444" // Cores de destaque (amarelo e vermelho)
          }
          return d.type === 'order' ? "#3b82f6" : "#10b981" // Cores padrão
        })
        .attr("stroke", (d: any) => d.highlighted ? "#fbbf24" : "#fff")
        .attr("stroke-width", (d: any) => d.highlighted ? 4 : 2)

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
        
      } catch (error) {
        console.error('❌ Erro ao inicializar NetworkGraph:', error)
        // Em caso de erro, tentar novamente após um delay maior
        setTimeout(initializeGraph, 500)
      }
    }

    // Inicializar com pequeno delay para garantir renderização
    setTimeout(initializeGraph, 50)

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
      <div className="absolute bottom-4 left-4 text-xs text-gray-500 bg-white bg-opacity-90 px-2 py-1 rounded max-w-md">
        <strong>Arraste:</strong> mover visualização • <strong>Roda do mouse:</strong> zoom • <strong>Clique nos nós:</strong> ações • <strong>Arraste nós:</strong> reposicionar
      </div>

      {/* Context Menu */}
      {contextMenu.visible && contextMenu.node && (
        <div 
          className="absolute bg-white rounded-lg shadow-xl border border-gray-200 py-1 min-w-52 backdrop-blur-sm"
          style={{ 
            left: contextMenu.x, 
            top: contextMenu.y,
            transform: 'translate(-50%, -10px)',
            zIndex: 9999,
            position: 'fixed',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
          }}
        >
          <div className="px-4 py-3 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-indigo-50">
            <div className="font-semibold text-gray-900 text-sm flex items-center gap-2">
              <span className="text-lg">{contextMenu.node.type === 'order' ? '📋' : '📄'}</span>
              <span className="truncate max-w-36">{contextMenu.node.label}</span>
            </div>
            <div className="text-xs text-gray-600 mt-1 font-medium">
              {contextMenu.node.type === 'order' ? 'Super-contêiner Logístico' : 'Documento Digital'}
            </div>
          </div>
          
          <div className="py-1">
            {contextMenu.node.type === 'document' && (
              <>
                <button
                  onClick={() => viewMetadata(contextMenu.node!)}
                  disabled={loading}
                  className="w-full px-4 py-3 text-left text-sm hover:bg-blue-50 hover:text-blue-700 flex items-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  <span className="text-blue-600">📄</span>
                  <div>
                    <div className="font-medium">Ver Metadados</div>
                    <div className="text-xs text-gray-500">Abrir JSON completo</div>
                  </div>
                </button>
                <button
                  onClick={() => downloadDocument(contextMenu.node!)}
                  disabled={loading}
                  className="w-full px-4 py-3 text-left text-sm hover:bg-green-50 hover:text-green-700 flex items-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  <span className="text-green-600">💾</span>
                  <div>
                    <div className="font-medium">Baixar Documento</div>
                    <div className="text-xs text-gray-500">Download do arquivo</div>
                  </div>
                </button>
              </>
            )}
            
            {contextMenu.node.type === 'order' && (
              <button
                onClick={() => viewOrder(contextMenu.node!)}
                disabled={loading}
                className="w-full px-4 py-3 text-left text-sm hover:bg-orange-50 hover:text-orange-700 flex items-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                <span className="text-orange-600">📋</span>
                <div>
                  <div className="font-medium">Ver Detalhes</div>
                  <div className="text-xs text-gray-500">Informações da Order</div>
                </div>
              </button>
            )}
          </div>
          
          <div className="border-t border-gray-100">
            <button
              onClick={closeContextMenu}
              className="w-full px-4 py-2 text-left text-sm text-gray-500 hover:bg-gray-50 hover:text-gray-700 transition-colors duration-200 flex items-center gap-2"
            >
              <span>✖️</span>
              <span>Fechar</span>
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
        style={{ minHeight: '400px' }}
      />
    </div>
  )
}