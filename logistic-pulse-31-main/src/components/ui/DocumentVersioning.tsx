import React, { useState } from "react";
import { Button } from "./button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./card";
import { Badge } from "./badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./select";
import { Input } from "./input";
import { Textarea } from "./textarea";
import { toast } from "./use-toast";
import { FileText, Plus, Download, Eye, Clock, User, CheckCircle, XCircle, AlertCircle } from "lucide-react";

interface DocumentVersion {
  version_id: string;
  version_number: string;
  changes_description: string;
  created_at: string;
  created_by: string;
  approval_status: "pending" | "approved" | "rejected";
  file_size?: number;
  checksum?: string;
}

interface DocumentVersioningProps {
  documentId: string;
  currentVersion: string;
  versions: DocumentVersion[];
  onCreateVersion: (data: {
    version_type: "major" | "minor" | "revision" | "auto";
    changes_description: string;
    file?: File;
  }) => Promise<void>;
  onViewVersion: (versionId: string) => void;
  onDownloadVersion: (versionId: string) => void;
  isLoading?: boolean;
}

const DocumentVersioning: React.FC<DocumentVersioningProps> = ({
  documentId,
  currentVersion,
  versions,
  onCreateVersion,
  onViewVersion,
  onDownloadVersion,
  isLoading = false
}) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [versionType, setVersionType] = useState<"major" | "minor" | "revision" | "auto">("auto");
  const [changesDescription, setChangesDescription] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [creating, setCreating] = useState(false);

  const handleCreateVersion = async () => {
    if (!changesDescription.trim()) {
      toast({
        title: "Erro",
        description: "Descrição das alterações é obrigatória",
        variant: "destructive",
      });
      return;
    }

    setCreating(true);
    try {
      await onCreateVersion({
        version_type: versionType,
        changes_description: changesDescription,
        file: selectedFile || undefined,
      });
      
      setShowCreateForm(false);
      setChangesDescription("");
      setSelectedFile(null);
      setVersionType("auto");
      
      toast({
        title: "Sucesso",
        description: "Nova versão criada com sucesso",
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Falha ao criar nova versão",
        variant: "destructive",
      });
    } finally {
      setCreating(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "approved":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "rejected":
        return <XCircle className="h-4 w-4 text-red-600" />;
      case "pending":
        return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "approved":
        return "bg-green-100 text-green-800 border-green-300";
      case "rejected":
        return "bg-red-100 text-red-800 border-red-300";
      case "pending":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "N/A";
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Controle de Versões
            </CardTitle>
            <CardDescription>
              Versão atual: <Badge variant="secondary">{currentVersion}</Badge>
            </CardDescription>
          </div>
          <Button
            onClick={() => setShowCreateForm(!showCreateForm)}
            disabled={isLoading}
            size="sm"
          >
            <Plus className="h-4 w-4 mr-2" />
            Nova Versão
          </Button>
        </CardHeader>

        {showCreateForm && (
          <CardContent className="border-t">
            <div className="space-y-4 pt-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Tipo de Versão</label>
                  <Select value={versionType} onValueChange={setVersionType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="auto">Automático</SelectItem>
                      <SelectItem value="major">Maior (x.0.0)</SelectItem>
                      <SelectItem value="minor">Menor (x.y.0)</SelectItem>
                      <SelectItem value="revision">Revisão (x.y.z)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Novo Arquivo (Opcional)</label>
                  <Input
                    type="file"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                    accept=".pdf,.xml,.jpg,.jpeg,.png"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Descrição das Alterações*</label>
                <Textarea
                  placeholder="Descreva as alterações realizadas nesta versão..."
                  value={changesDescription}
                  onChange={(e) => setChangesDescription(e.target.value)}
                  rows={3}
                />
              </div>

              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowCreateForm(false)}
                  disabled={creating}
                >
                  Cancelar
                </Button>
                <Button
                  onClick={handleCreateVersion}
                  disabled={creating || !changesDescription.trim()}
                >
                  {creating ? "Criando..." : "Criar Versão"}
                </Button>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      <div className="space-y-2">
        <h3 className="text-lg font-medium">Histórico de Versões</h3>
        {versions.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500">Nenhuma versão adicional encontrada</p>
            </CardContent>
          </Card>
        ) : (
          versions.map((version) => (
            <Card key={version.version_id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline" className="font-mono">
                        v{version.version_number}
                      </Badge>
                      <Badge className={getStatusColor(version.approval_status)}>
                        <span className="flex items-center gap-1">
                          {getStatusIcon(version.approval_status)}
                          {version.approval_status === "pending" ? "Pendente" : 
                           version.approval_status === "approved" ? "Aprovado" : "Rejeitado"}
                        </span>
                      </Badge>
                      {version.version_number === currentVersion && (
                        <Badge variant="default">Atual</Badge>
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">
                      {version.changes_description}
                    </p>
                    
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <User className="h-3 w-3" />
                        {version.created_by}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(version.created_at).toLocaleString('pt-BR')}
                      </span>
                      {version.file_size && (
                        <span>{formatFileSize(version.file_size)}</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex gap-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onViewVersion(version.version_id)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onDownloadVersion(version.version_id)}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default DocumentVersioning;