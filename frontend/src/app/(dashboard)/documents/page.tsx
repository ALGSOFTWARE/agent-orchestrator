'use client'

import { useState } from 'react'
import { DocumentUpload } from '@/components/features/DocumentUpload'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import styles from '@/styles/pages/DocumentsPage.module.css'

interface UploadedDocument {
  id: string
  name: string
  size: number
  type: string
  url: string
  uploadedAt: string
  category: 'cte' | 'bl' | 'invoice' | 'other'
}

interface FileFromUploader {
    id: string;
    name: string;
    size: number;
    type: string;
    status: 'uploading' | 'completed' | 'error';
    url?: string;
}

export default function DocumentsPage() {
  const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDocument[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const handleFileUploaded = (file: FileFromUploader) => {
    if (file.status === 'completed' && file.url) {
      let category: UploadedDocument['category'] = 'other'
      const fileName = file.name.toLowerCase()
      
      if (fileName.includes('cte') || fileName.includes('conhecimento')) {
        category = 'cte'
      } else if (fileName.includes('bl') || fileName.includes('lading')) {
        category = 'bl'
      } else if (fileName.includes('invoice') || fileName.includes('fatura')) {
        category = 'invoice'
      }

      const document: UploadedDocument = {
        id: file.id,
        name: file.name,
        size: file.size,
        type: file.type,
        url: file.url,
        uploadedAt: new Date().toISOString(),
        category
      }

      setUploadedDocuments(prev => [document, ...prev])
    }
  }

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'cte': return '📄 CT-e'
      case 'bl': return '🚢 BL'
      case 'invoice': return '💰 Faturas'
      case 'other': return '📁 Outros'
      default: return '📋 Todos'
    }
  }

  const getCategoryIcon = (category: UploadedDocument['category']) => {
    switch (category) {
      case 'cte': return '📄'
      case 'bl': return '🚢'
      case 'invoice': return '💰'
      default: return '📁'
    }
  }

  const filteredDocuments = selectedCategory === 'all' 
    ? uploadedDocuments 
    : uploadedDocuments.filter(doc => doc.category === selectedCategory)

  const categoryCounts = {
    all: uploadedDocuments.length,
    cte: uploadedDocuments.filter(d => d.category === 'cte').length,
    bl: uploadedDocuments.filter(d => d.category === 'bl').length,
    invoice: uploadedDocuments.filter(d => d.category === 'invoice').length,
    other: uploadedDocuments.filter(d => d.category === 'other').length,
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (isoString: string): string => {
    return new Date(isoString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className={styles.documentsPage}>
      <div className={styles.header}>
        <h1>📁 Gestão de Documentos</h1>
        <p>Upload e gerenciamento de documentos logísticos</p>
      </div>

      {/* Upload Section */}
      <section className={styles.uploadSection}>
        <Card>
          <h2>📤 Upload de Documentos</h2>
          <p>Envie CT-es, BLs, faturas e outros documentos logísticos</p>
          
          <DocumentUpload
            onFileUploaded={handleFileUploaded}
            acceptedTypes={['.pdf', '.xml', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.json']}
            maxSizeBytes={25 * 1024 * 1024} // 25MB
            maxFiles={10}
          />
        </Card>
      </section>

      {/* Documents Library */}
      {uploadedDocuments.length > 0 && (
        <section className={styles.librarySection}>
          <Card>
            <div className={styles.libraryHeader}>
              <h2>📚 Biblioteca de Documentos</h2>
              <div className={styles.totalCount}>
                {uploadedDocuments.length} documento{uploadedDocuments.length !== 1 ? 's' : ''}
              </div>
            </div>

            {/* Category Filters */}
            <div className={styles.categoryFilters}>
              {Object.entries(categoryCounts).map(([category, count]) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(category)}
                  className={styles.categoryFilter}
                >
                  {getCategoryLabel(category)} ({count})
                </Button>
              ))}
            </div>

            {/* Documents Grid */}
            <div className={styles.documentsGrid}>
              {filteredDocuments.map((document) => (
                <Card key={document.id} className={styles.documentCard}>
                  <div className={styles.documentHeader}>
                    <div className={styles.documentIcon}>
                      {getCategoryIcon(document.category)}
                    </div>
                    <div className={styles.categoryBadge}>
                      {getCategoryLabel(document.category)}
                    </div>
                  </div>

                  <div className={styles.documentInfo}>
                    <h3 className={styles.documentName} title={document.name}>
                      {document.name}
                    </h3>
                    
                    <div className={styles.documentMeta}>
                      <span className={styles.documentSize}>
                        {formatFileSize(document.size)}
                      </span>
                      <span className={styles.documentDate}>
                        {formatDate(document.uploadedAt)}
                      </span>
                    </div>
                  </div>

                  <div className={styles.documentActions}>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        const viewUrl = `http://localhost:8001/files/${document.id}/view`
                        window.open(viewUrl, '_blank', 'noopener,noreferrer')
                      }}
                      className={styles.viewButton}
                    >
                      👁️ Ver
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        // Usar endpoint /view para download/visualização
                        const viewUrl = `http://localhost:8001/files/${document.id}/view`
                        window.open(viewUrl, '_blank', 'noopener,noreferrer')
                      }}
                      className={styles.downloadButton}
                    >
                      📥 Download
                    </Button>
                  </div>
                </Card>
              ))}
            </div>

            {filteredDocuments.length === 0 && (
              <div className={styles.emptyState}>
                <div className={styles.emptyIcon}>📂</div>
                <h3>Nenhum documento encontrado</h3>
                <p>
                  {selectedCategory === 'all' 
                    ? 'Faça upload de alguns documentos para começar'
                    : `Nenhum documento na categoria "${getCategoryLabel(selectedCategory)}"`
                  }
                </p>
              </div>
            )}
          </Card>
        </section>
      )}

      {/* Usage Tips */}
      <section className={styles.tipsSection}>
        <Card>
          <h3>💡 Dicas de Uso</h3>
          <div className={styles.tips}>
            <div className={styles.tip}>
              <span className={styles.tipIcon}>📄</span>
              <div>
                <strong>CT-e:</strong> Conhecimentos de Transporte Eletrônico em PDF ou XML
              </div>
            </div>
            <div className={styles.tip}>
              <span className={styles.tipIcon}>🚢</span>
              <div>
                <strong>BL:</strong> Bills of Lading para transporte marítimo
              </div>
            </div>
            <div className={styles.tip}>
              <span className={styles.tipIcon}>💰</span>
              <div>
                <strong>Faturas:</strong> Documentos financeiros e de cobrança
              </div>
            </div>
            <div className={styles.tip}>
              <span className={styles.tipIcon}>🔍</span>
              <div>
                <strong>OCR:</strong> Documentos em imagem são processados automaticamente
              </div>
            </div>
          </div>
        </Card>
      </section>
    </div>
  )
}