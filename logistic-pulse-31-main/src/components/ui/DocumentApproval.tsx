import React, { useState } from "react";
import { Button } from "./button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./card";
import { Badge } from "./badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./select";
import { Textarea } from "./textarea";
import { toast } from "./use-toast";
import { CheckCircle, XCircle, AlertCircle, Clock, User, MessageSquare, Send } from "lucide-react";

interface ApprovalComment {
  comment_id: string;
  approver_id: string;
  approver_name: string;
  comment: string;
  decision: "approved" | "rejected" | "request_changes";
  created_at: string;
}

interface DocumentApproval {
  approval_id: string;
  document_id: string;
  version_id: string;
  workflow_id: string;
  current_level: number;
  total_levels: number;
  overall_status: "pending" | "approved" | "rejected";
  current_approver_id?: string;
  current_approver_name?: string;
  created_at: string;
  completed_at?: string;
  comments: ApprovalComment[];
}

interface DocumentApprovalProps {
  documentId: string;
  versionId?: string;
  approval?: DocumentApproval;
  canApprove?: boolean;
  currentUserId?: string;
  onSubmitApproval: (decision: "approved" | "rejected" | "request_changes", comment: string) => Promise<void>;
  onRequestApproval: (workflowId: string) => Promise<void>;
  isLoading?: boolean;
}

const DocumentApproval: React.FC<DocumentApprovalProps> = ({
  documentId,
  versionId,
  approval,
  canApprove = false,
  currentUserId,
  onSubmitApproval,
  onRequestApproval,
  isLoading = false
}) => {
  const [decision, setDecision] = useState<"approved" | "rejected" | "request_changes">("approved");
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState("");

  const handleSubmitApproval = async () => {
    if (!comment.trim()) {
      toast({
        title: "Erro",
        description: "Comentário é obrigatório",
        variant: "destructive",
      });
      return;
    }

    setSubmitting(true);
    try {
      await onSubmitApproval(decision, comment);
      setComment("");
      toast({
        title: "Sucesso",
        description: "Aprovação registrada com sucesso",
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Falha ao registrar aprovação",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleRequestApproval = async () => {
    if (!selectedWorkflow) {
      toast({
        title: "Erro",
        description: "Selecione um workflow de aprovação",
        variant: "destructive",
      });
      return;
    }

    try {
      await onRequestApproval(selectedWorkflow);
      setShowRequestForm(false);
      setSelectedWorkflow("");
      toast({
        title: "Sucesso",
        description: "Aprovação solicitada com sucesso",
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Falha ao solicitar aprovação",
        variant: "destructive",
      });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "approved":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "rejected":
        return <XCircle className="h-4 w-4 text-red-600" />;
      case "request_changes":
        return <AlertCircle className="h-4 w-4 text-orange-600" />;
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-600" />;
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
      case "request_changes":
        return "bg-orange-100 text-orange-800 border-orange-300";
      case "pending":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const getDecisionLabel = (decision: string) => {
    switch (decision) {
      case "approved":
        return "Aprovado";
      case "rejected":
        return "Rejeitado";
      case "request_changes":
        return "Solicitação de Alterações";
      default:
        return decision;
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5" />
              Aprovação do Documento
            </CardTitle>
            {approval ? (
              <CardDescription>
                Nível {approval.current_level} de {approval.total_levels} - 
                Status: <Badge className={getStatusColor(approval.overall_status)}>
                  <span className="flex items-center gap-1">
                    {getStatusIcon(approval.overall_status)}
                    {approval.overall_status === "pending" ? "Pendente" : 
                     approval.overall_status === "approved" ? "Aprovado" : "Rejeitado"}
                  </span>
                </Badge>
              </CardDescription>
            ) : (
              <CardDescription>Nenhum processo de aprovação iniciado</CardDescription>
            )}
          </div>
          {!approval && (
            <Button
              onClick={() => setShowRequestForm(!showRequestForm)}
              disabled={isLoading}
              size="sm"
            >
              <Send className="h-4 w-4 mr-2" />
              Solicitar Aprovação
            </Button>
          )}
        </CardHeader>

        {showRequestForm && (
          <CardContent className="border-t">
            <div className="space-y-4 pt-4">
              <div>
                <label className="text-sm font-medium">Workflow de Aprovação</label>
                <Select value={selectedWorkflow} onValueChange={setSelectedWorkflow}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione um workflow..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="standard">Aprovação Padrão (1 nível)</SelectItem>
                    <SelectItem value="multi_level">Aprovação Multi-nível (3 níveis)</SelectItem>
                    <SelectItem value="financial">Aprovação Financeira (2 níveis)</SelectItem>
                    <SelectItem value="compliance">Aprovação Compliance (4 níveis)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowRequestForm(false)}
                >
                  Cancelar
                </Button>
                <Button
                  onClick={handleRequestApproval}
                  disabled={!selectedWorkflow}
                >
                  Solicitar
                </Button>
              </div>
            </div>
          </CardContent>
        )}

        {approval && canApprove && approval.current_approver_id === currentUserId && (
          <CardContent className="border-t">
            <div className="space-y-4 pt-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Sua aprovação é necessária.</strong> Como aprovador do nível {approval.current_level}, 
                  você pode aprovar, rejeitar ou solicitar alterações neste documento.
                </p>
              </div>

              <div>
                <label className="text-sm font-medium">Decisão</label>
                <Select value={decision} onValueChange={setDecision}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="approved">Aprovar</SelectItem>
                    <SelectItem value="request_changes">Solicitar Alterações</SelectItem>
                    <SelectItem value="rejected">Rejeitar</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Comentário*</label>
                <Textarea
                  placeholder="Adicione seus comentários sobre a aprovação..."
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  rows={3}
                />
              </div>

              <div className="flex justify-end">
                <Button
                  onClick={handleSubmitApproval}
                  disabled={submitting || !comment.trim()}
                >
                  {submitting ? "Enviando..." : "Enviar Decisão"}
                </Button>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {approval && approval.comments.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Histórico de Comentários
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {approval.comments.map((comment) => (
                <div key={comment.comment_id} className="border-l-4 border-gray-200 pl-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(comment.decision)}>
                        <span className="flex items-center gap-1">
                          {getStatusIcon(comment.decision)}
                          {getDecisionLabel(comment.decision)}
                        </span>
                      </Badge>
                      <span className="text-sm font-medium">{comment.approver_name}</span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(comment.created_at).toLocaleString('pt-BR')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{comment.comment}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {approval && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Informações do Processo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Processo iniciado:</span>
                <p>{new Date(approval.created_at).toLocaleString('pt-BR')}</p>
              </div>
              {approval.completed_at && (
                <div>
                  <span className="text-gray-500">Concluído em:</span>
                  <p>{new Date(approval.completed_at).toLocaleString('pt-BR')}</p>
                </div>
              )}
              <div>
                <span className="text-gray-500">Aprovador atual:</span>
                <p>{approval.current_approver_name || "N/A"}</p>
              </div>
              <div>
                <span className="text-gray-500">Progresso:</span>
                <p>{approval.current_level} de {approval.total_levels} níveis</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DocumentApproval;