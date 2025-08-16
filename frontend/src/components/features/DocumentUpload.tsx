'use client'

import { useState, useCallback } from 'react'
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
}

export function DocumentUpload({
  onFileUploaded,
  acceptedTypes = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.xml', '.json'],
  maxSizeBytes = 10 * 1024 * 1024, // 10MB
  maxFiles = 5
}: DocumentUploadProps) {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isDragOver, setIsDragOver] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const validateFile = (file: File): string | null => {
    // Check file size
    if (file.size > maxSizeBytes) {
      return `Arquivo muito grande. Máximo permitido: ${formatFileSize(maxSizeBytes)}`
    }

    // Check file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!acceptedTypes.includes(fileExtension || '')) {
      return `Tipo de arquivo não permitido. Aceitos: ${acceptedTypes.join(', ')}`
    }

    // Check max files
    if (files.length >= maxFiles) {
      return `Máximo de ${maxFiles} arquivos permitidos`
    }

    return null
  }

  const simulateUpload = async (file: File): Promise<UploadedFile> => {
    const uploadedFile: UploadedFile = {
      id: `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: file.name,
      size: file.size,
      type: file.type,
      uploadProgress: 0,
      status: 'uploading'
    }

    // Simulate upload progress
    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise(resolve => setTimeout(resolve, 100))
      
      setFiles(prev => prev.map(f => 
        f.id === uploadedFile.id 
          ? { ...f, uploadProgress: progress }
          : f
      ))
    }

    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 500))

    // Mock successful upload
    const completedFile: UploadedFile = {
      ...uploadedFile,
      uploadProgress: 100,
      status: 'completed',
      url: `https://mock-storage.com/documents/${uploadedFile.id}/${file.name}`
    }

    return completedFile
  }

  const uploadFile = async (file: File) => {
    const validation = validateFile(file)
    if (validation) {
      alert(validation)
      return
    }

    const uploadedFile: UploadedFile = {
      id: `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: file.name,
      size: file.size,
      type: file.type,
      uploadProgress: 0,
      status: 'uploading'
    }

    setFiles(prev => [...prev, uploadedFile])
    setIsUploading(true)

    try {
      const completedFile = await simulateUpload(file)
      
      setFiles(prev => prev.map(f => 
        f.id === uploadedFile.id ? completedFile : f
      ))

      onFileUploaded?.(completedFile)
    } catch (error) {
      const errorFile: UploadedFile = {
        ...uploadedFile,
        status: 'error',
        error: error instanceof Error ? error.message : 'Erro no upload'
      }

      setFiles(prev => prev.map(f => 
        f.id === uploadedFile.id ? errorFile : f
      ))
    } finally {
      setIsUploading(false)
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || [])
    selectedFiles.forEach(uploadFile)
    event.target.value = '' // Reset input
  }

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    setIsDragOver(false)

    const droppedFiles = Array.from(event.dataTransfer.files)
    droppedFiles.forEach(uploadFile)
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

  const retryUpload = (fileId: string) => {
    const fileToRetry = files.find(f => f.id === fileId)
    if (fileToRetry) {
      // For retry, we'd need to store the original File object
      // For now, just remove the failed file
      removeFile(fileId)
    }
  }

  return (
    <div className={styles.documentUpload}>
      {/* Upload Area */}
      <div
        className={`${styles.uploadArea} ${
          isDragOver ? styles.dragOver : ''
        }`}
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
            disabled={isUploading || files.length >= maxFiles}
          />
          
          <Button
            as="label"
            htmlFor="file-upload"
            disabled={isUploading || files.length >= maxFiles}
            className={styles.uploadButton}
          >
            {isUploading ? 'Enviando...' : 'Selecionar Arquivos'}
          </Button>
        </div>
      </div>

      {/* File List */}
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

              {/* Progress Bar */}
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

              {/* Status */}
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
                      onClick={() => retryUpload(file.id)}
                      className={styles.retryButton}
                    >
                      Tentar novamente
                    </Button>
                  </div>
                )}

                {file.status === 'uploading' && (
                  <div className={styles.statusUploading}>
                    <span>⏳ Enviando...</span>
                  </div>
                )}
              </div>

              {/* Remove Button */}
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

      {/* Upload Summary */}
      {files.length > 0 && (
        <div className={styles.uploadSummary}>
          <Card>
            <h4>📊 Resumo do Upload</h4>
            <div className={styles.summaryStats}>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Total de arquivos:</span>
                <span className={styles.statValue}>{files.length}</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Concluídos:</span>
                <span className={styles.statValue}>
                  {files.filter(f => f.status === 'completed').length}
                </span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Com erro:</span>
                <span className={styles.statValue}>
                  {files.filter(f => f.status === 'error').length}
                </span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Tamanho total:</span>
                <span className={styles.statValue}>
                  {formatFileSize(files.reduce((sum, f) => sum + f.size, 0))}
                </span>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}