'use client'

import { useState, useCallback, useEffect } from 'react'
import { uploadFile } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import styles from '@/styles/modules/DocumentUpload.module.css'

interface UploadedFile {
  id: string
  name: string
  size: number
  type: string
  uploadProgress: number
  status: 'uploading' | 'completed' | 'error'
  url?: string
  error?: string
  order_id?: string
  order_title?: string
  processing_result?: any
  extracted_text?: string
}

interface Order {
  _id: string
  order_id: string
  title: string
  customer_name: string
  order_type: string
  status: string
}

interface DocumentUploadProps {
  onFileUploaded?: (file: UploadedFile) => void
  acceptedTypes?: string[]
  maxSizeBytes?: number
  maxFiles?: number
  publicUpload?: boolean
}

export function DocumentUpload({
  onFileUploaded,
  acceptedTypes = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.xml', '.json'],
  maxSizeBytes = 10 * 1024 * 1024, // 10MB
  maxFiles = 5,
  publicUpload = true // Por padrão, faz upload público para evitar problemas de acesso
}: DocumentUploadProps) {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isDragOver, setIsDragOver] = useState(false)
  const [orders, setOrders] = useState<Order[]>([])
  const [selectedOrderId, setSelectedOrderId] = useState<string>('')
  const [isLoadingOrders, setIsLoadingOrders] = useState(true)
  const [showTextModal, setShowTextModal] = useState(false)
  const [currentTextContent, setCurrentTextContent] = useState('')
  const [currentFileName, setCurrentFileName] = useState('')

  // Carregar Orders disponíveis
  useEffect(() => {
    const fetchOrders = async () => {
      try {
        console.log('🔄 Fetching orders from API...')
        const response = await fetch('http://localhost:8001/orders/')
        const ordersData = await response.json()
        console.log('📋 Orders received:', ordersData.length, ordersData)
        setOrders(ordersData)
        // Auto-selecionar primeira Order se houver
        if (ordersData.length > 0) {
          const firstOrderId = ordersData[0].order_id
          console.log('✅ Auto-selecting first order:', firstOrderId)
          setSelectedOrderId(firstOrderId)
        } else {
          console.warn('⚠️ No orders found')
        }
      } catch (error) {
        console.error('❌ Erro ao carregar Orders:', error)
      } finally {
        setIsLoadingOrders(false)
      }
    }
    
    fetchOrders()
  }, [])

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const validateFile = (file: File): string | null => {
    console.log('🔍 Validating file:', file.name, 'selectedOrderId:', selectedOrderId)
    if (!selectedOrderId) {
      console.error('❌ No order selected!')
      return 'Selecione uma Order antes de fazer upload. Todo documento deve estar vinculado a uma Order.'
    }
    if (file.size > maxSizeBytes) {
      return `Arquivo muito grande. Máximo permitido: ${formatFileSize(maxSizeBytes)}`
    }
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!acceptedTypes.includes(fileExtension || '')) {
      return `Tipo de arquivo não permitido. Aceitos: ${acceptedTypes.join(', ')}`
    }
    if (files.length >= maxFiles) {
      return `Máximo de ${maxFiles} arquivos permitidos`
    }
    return null
  }

  const handleUpload = useCallback(async (file: File) => {
    const validationError = validateFile(file)
    if (validationError) {
      alert(validationError)
      return
    }

    const tempId = `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const newFile: UploadedFile = {
      id: tempId,
      name: file.name,
      size: file.size,
      type: file.type,
      uploadProgress: 0,
      status: 'uploading',
    }
    setFiles(prev => [...prev, newFile])

    try {
      // Construir URL com parâmetros obrigatórios (order_id) e opcionais
      const params = new URLSearchParams({
        order_id: selectedOrderId,
        public: publicUpload.toString()
      })
      const uploadUrl = `/files/upload?${params.toString()}`
      
      const response = await uploadFile(file, uploadUrl, (progress) => {
        setFiles(prev => prev.map(f => f.id === tempId ? { ...f, uploadProgress: progress } : f))
      })

      console.log('📤 Upload response:', response)
      console.log('🧠 Intelligent processing:', (response as any).intelligent_processing)
      console.log('🔍 Full response keys:', Object.keys(response))
      console.log('🔍 Response type:', typeof response)

      const completedFile: UploadedFile = {
        ...newFile,
        id: response.id, // Use o ID real do backend
        status: 'completed',
        uploadProgress: 100,
        url: response.url,
        order_id: response.order_id,
        order_title: response.order_title,
        processing_result: (response as any).intelligent_processing?.result || (response as any).intelligent_processing,
        extracted_text: ((response as any).intelligent_processing?.result?.text_length || (response as any).intelligent_processing?.ocr_available) ? 'Texto extraído disponível' : ''
      }
      
      console.log('✅ Completed file object:', completedFile)
      setFiles(prev => prev.map(f => f.id === tempId ? completedFile : f))
      onFileUploaded?.(completedFile)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro no upload'
      setFiles(prev => prev.map(f => f.id === tempId ? { ...f, status: 'error', error: errorMessage } : f))
    }
  }, [selectedOrderId, publicUpload, onFileUploaded])

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || [])
    selectedFiles.forEach(handleUpload)
    event.target.value = '' // Reset input
  }, [handleUpload])

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    setIsDragOver(false)
    const droppedFiles = Array.from(event.dataTransfer.files)
    droppedFiles.forEach(handleUpload)
  }, [handleUpload])

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    setIsDragOver(false)
  }, [])

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const viewExtractedText = async (file: UploadedFile) => {
    try {
      console.log('🔍 Fetching extracted text for:', file.id)
      
      // Primeira tentativa: usar dados de processamento já disponíveis
      if (file.processing_result && file.processing_result.text_length > 0) {
        // Buscar metadados completos com o texto
        const response = await fetch(`http://localhost:8001/files/${file.id}/metadata`)
        const metadata = await response.json()
        
        console.log('📄 Metadata received:', metadata)
        
        // Verificar se o texto está disponível nos metadados
        if (metadata.document && metadata.document.text_content_length > 0) {
          // Como não temos endpoint /text, vamos buscar o documento completo via MongoDB
          // Por enquanto, vamos mostrar um resumo baseado nos dados disponíveis
          const summaryText = `
=== RESUMO DO PROCESSAMENTO OCR ===
Arquivo: ${file.name}
Tamanho do texto extraído: ${file.processing_result.text_length} caracteres
Sentenças encontradas: ${file.processing_result.sentences || 'N/A'}

=== ENTIDADES LOGÍSTICAS ENCONTRADAS ===
${file.processing_result.logistics_entities?.map((entity: any) => 
  `${entity.type}: ${entity.value}`
).join('\n') || 'Nenhuma entidade específica encontrada'}

=== INFORMAÇÕES TÉCNICAS ===
Confiança do processamento: ${file.processing_result.confidence || 'N/A'}
Provedor de embedding: ${metadata.embedding_provider || 'N/A'}
Status: ${metadata.document.processing_status || 'N/A'}

Nota: Para visualizar o texto completo, será necessário implementar 
endpoint específico na API ou acessar diretamente via MongoDB.
          `
          setCurrentTextContent(summaryText)
        } else {
          setCurrentTextContent('Texto foi processado mas não está disponível nos metadados.')
        }
      } else {
        setCurrentTextContent('Nenhum texto foi extraído deste documento pelo OCR.')
      }
      
      setCurrentFileName(file.name)
      setShowTextModal(true)
    } catch (error) {
      console.error('Erro ao buscar texto:', error)
      setCurrentTextContent(`Erro ao carregar informações: ${error}`)
      setCurrentFileName(file.name)
      setShowTextModal(true)
    }
  }

  return (
    <div className={styles.documentUpload}>
      {/* Seleção de Order - Conceito Mapa Mental */}
      <Card className={styles.orderSelection}>
        <div className={styles.orderSelectionHeader}>
          <h3>📋 Vincular Documento à Order</h3>
          <p>Todo documento deve estar obrigatoriamente vinculado a uma Order (conceito mapa mental)</p>
        </div>
        
        {isLoadingOrders ? (
          <div className={styles.loading}>Carregando Orders...</div>
        ) : orders.length === 0 ? (
          <div className={styles.noOrders}>
            <p>❌ Nenhuma Order encontrada. Crie uma Order primeiro em:</p>
            <Button onClick={() => window.location.href = '/orders'}>
              Gerenciar Orders
            </Button>
          </div>
        ) : (
          <div className={styles.orderSelectContainer}>
            <label htmlFor="order-select" className={styles.orderLabel}>
              Selecionar Order:
            </label>
            <select
              id="order-select"
              value={selectedOrderId}
              onChange={(e) => setSelectedOrderId(e.target.value)}
              className={styles.orderSelect}
            >
              <option value="">Selecione uma Order...</option>
              {orders.map((order) => (
                <option key={order.order_id} value={order.order_id}>
                  {order.title} - {order.customer_name} ({order.order_type})
                </option>
              ))}
            </select>
            
            {selectedOrderId && (
              <div className={styles.selectedOrderInfo}>
                {(() => {
                  const selectedOrder = orders.find(o => o.order_id === selectedOrderId)
                  return selectedOrder ? (
                    <div className={styles.orderInfo}>
                      <span className={styles.orderIcon}>🎯</span>
                      <div>
                        <strong>{selectedOrder.title}</strong>
                        <br />
                        <small>{selectedOrder.customer_name} • {selectedOrder.status}</small>
                      </div>
                    </div>
                  ) : null
                })()}
              </div>
            )}
          </div>
        )}
      </Card>

      <div
        className={`${styles.uploadArea} ${isDragOver ? styles.dragOver : ''} ${!selectedOrderId ? styles.disabled : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className={styles.uploadContent}>
          <div className={styles.uploadIcon}>📁</div>
          {selectedOrderId ? (
            <>
              <h3>Arraste arquivos aqui ou clique para selecionar</h3>
              <p>
                Tipos aceitos: {acceptedTypes.join(', ')}<br />
                Tamanho máximo: {formatFileSize(maxSizeBytes)} por arquivo<br />
                <strong>🎯 Vinculado à Order selecionada</strong>
              </p>
            </>
          ) : (
            <>
              <h3>Selecione uma Order primeiro</h3>
              <p>
                ⚠️ Todo documento deve estar vinculado a uma Order.<br />
                Selecione uma Order acima para continuar.
              </p>
            </>
          )}
          
          <input
            type="file"
            multiple
            accept={acceptedTypes.join(',')}
            onChange={handleFileSelect}
            className={styles.fileInput}
            id="file-upload"
            disabled={files.some(f => f.status === 'uploading')}
          />
          
          <label 
            htmlFor="file-upload"
            className={`${styles.uploadButton} ${files.some(f => f.status === 'uploading') ? styles.disabled : ''}`}
          >
            {files.some(f => f.status === 'uploading') ? 'Enviando...' : 'Selecionar Arquivos'}
          </label>
        </div>
      </div>

      {files.length > 0 && (
        <div className={styles.fileList}>
          <h4>📋 Arquivos ({files.length}/{maxFiles})</h4>
          
          {files.map((file) => (
            <Card key={file.id} className={styles.fileItem}>
              <div className={styles.fileInfo}>
                <div className={styles.fileName}>
                  <span className={styles.fileIcon}>
                    {file.type.startsWith('image/') ? '🖼️' : 
                     file.name.endsWith('.pdf') ? '📄' : 
                     file.name.endsWith('.xml') ? '📋' : 
                     file.name.endsWith('.json') ? '📊' : '📁'}
                  </span>
                  <span>{file.name}</span>
                </div>
                <div className={styles.fileSize}>
                  {formatFileSize(file.size)}
                </div>
              </div>

              {file.status === 'uploading' && (
                <div className={styles.progressContainer}>
                  <div className={styles.progressBar}>
                    <div 
                      className={styles.progressFill}
                      style={{ width: `${file.uploadProgress}%` }}
                    />
                  </div>
                  <span className={styles.progressText}>
                    {file.uploadProgress}%
                  </span>
                </div>
              )}

              <div className={styles.fileStatus}>
                {file.status === 'completed' && (
                  <div className={styles.statusSuccess}>
                    <span>✅ Upload concluído</span>
                    {file.order_title && (
                      <div className={styles.orderLink}>
                        📋 Vinculado à: <strong>{file.order_title}</strong>
                      </div>
                    )}
                    {file.url && (
                      <a 
                        href={file.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className={styles.fileLink}
                      >
                        Ver arquivo
                      </a>
                    )}
                    {(() => {
                      console.log('🔍 Rendering file:', file.name, 'processing_result:', file.processing_result)
                      console.log('🔍 File status:', file.status, 'ID:', file.id)
                      
                      // Mostrar botão sempre que o arquivo estiver completo
                      if (file.status === 'completed') {
                        return (
                          <div className={styles.ocrResults}>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => viewExtractedText(file)}
                              className={styles.viewTextButton}
                            >
                              📄 Ver Resultado do OCR ({file.processing_result?.text_length || '?'} chars)
                            </Button>
                            {file.processing_result?.logistics_entities?.length > 0 && (
                              <div className={styles.entitiesFound}>
                                🏷️ {file.processing_result.logistics_entities.length} entidades logísticas encontradas
                              </div>
                            )}
                            {!file.processing_result && (
                              <div style={{color: 'blue', fontSize: '12px'}}>
                                💡 Clique para ver os dados de processamento disponíveis
                              </div>
                            )}
                          </div>
                        )
                      } else {
                        return (
                          <div style={{color: 'orange', fontSize: '12px'}}>
                            ⏳ Processando documento...
                          </div>
                        )
                      }
                    })()}
                  </div>
                )}

                {file.status === 'error' && (
                  <div className={styles.statusError}>
                    <span>❌ {file.error}</span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeFile(file.id)} // Simplificado para remover
                      className={styles.retryButton}
                    >
                      Limpar
                    </Button>
                  </div>
                )}
              </div>

              <Button
                size="sm"
                variant="ghost"
                onClick={() => removeFile(file.id)}
                className={styles.removeButton}
                title="Remover arquivo"
              >
                🗑️
              </Button>
            </Card>
          ))}
        </div>
      )}

      {/* Modal de Visualização de Texto */}
      {showTextModal && (
        <div className={styles.textModal}>
          <div className={styles.textModalContent}>
            <div className={styles.textModalHeader}>
              <h3>📄 Texto Extraído: {currentFileName}</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowTextModal(false)}
                className={styles.closeModal}
              >
                ✕
              </Button>
            </div>
            <div className={styles.textModalBody}>
              <pre className={styles.extractedText}>
                {currentTextContent}
              </pre>
            </div>
            <div className={styles.textModalFooter}>
              <Button
                variant="outline"
                onClick={() => {
                  navigator.clipboard.writeText(currentTextContent)
                  alert('Texto copiado para a área de transferência!')
                }}
              >
                📋 Copiar Texto
              </Button>
              <Button
                variant="secondary"
                onClick={() => setShowTextModal(false)}
              >
                Fechar
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
