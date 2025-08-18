'use client'

import { useState, useCallback } from 'react'
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

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const validateFile = (file: File): string | null => {
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

  const handleUpload = async (file: File) => {
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
      // Construir URL com parâmetro public se necessário
      const uploadUrl = `/files/upload${publicUpload ? '?public=true' : ''}`
      
      const response = await uploadFile(file, uploadUrl, (progress) => {
        setFiles(prev => prev.map(f => f.id === tempId ? { ...f, uploadProgress: progress } : f))
      })

      const completedFile: UploadedFile = {
        ...newFile,
        id: response.id, // Use o ID real do backend
        status: 'completed',
        uploadProgress: 100,
        url: response.url,
      }
      setFiles(prev => prev.map(f => f.id === tempId ? completedFile : f))
      onFileUploaded?.(completedFile)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro no upload'
      setFiles(prev => prev.map(f => f.id === tempId ? { ...f, status: 'error', error: errorMessage } : f))
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || [])
    selectedFiles.forEach(handleUpload)
    event.target.value = '' // Reset input
  }

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    setIsDragOver(false)
    const droppedFiles = Array.from(event.dataTransfer.files)
    droppedFiles.forEach(handleUpload)
  }, [files, maxFiles, maxSizeBytes, acceptedTypes])

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

  return (
    <div className={styles.documentUpload}>
      <div
        className={`${styles.uploadArea} ${isDragOver ? styles.dragOver : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className={styles.uploadContent}>
          <div className={styles.uploadIcon}>📁</div>
          <h3>Arraste arquivos aqui ou clique para selecionar</h3>
          <p>
            Tipos aceitos: {acceptedTypes.join(', ')}<br />
            Tamanho máximo: {formatFileSize(maxSizeBytes)} por arquivo
          </p>
          
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
    </div>
  )
}
