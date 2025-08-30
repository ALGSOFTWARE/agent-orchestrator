import React from "react";
import { Button } from "./button";

interface DocumentViewerProps {
  tipo: "PDF" | "XML" | "IMAGEM";
  url: string;
  nome: string;
  status?: string;
  data?: string;
  enviadoPor?: string;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ tipo, url, nome, status, data, enviadoPor }) => {
  return (
    <div className="w-full max-w-2xl mx-auto bg-background rounded-lg shadow-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">{nome}</h2>
          {status && <span className="text-xs text-muted-foreground mr-2">Status: {status}</span>}
          {data && <span className="text-xs text-muted-foreground mr-2">Data: {data}</span>}
          {enviadoPor && <span className="text-xs text-muted-foreground">Enviado por: {enviadoPor}</span>}
        </div>
        <Button asChild variant="outline" size="sm">
          <a href={url} download target="_blank" rel="noopener noreferrer">Baixar</a>
        </Button>
      </div>
      <div className="w-full min-h-[400px] flex items-center justify-center bg-muted rounded">
        {tipo === "PDF" && (
          <iframe
            src={url}
            title={nome}
            className="w-full h-[500px] rounded border"
            style={{ minHeight: 400 }}
          />
        )}
        {tipo === "XML" && (
          <iframe
            src={url}
            title={nome}
            className="w-full h-[500px] rounded border bg-white"
            style={{ minHeight: 400 }}
          />
        )}
        {tipo === "IMAGEM" && (
          <img
            src={url}
            alt={nome}
            className="max-h-[500px] w-auto rounded shadow"
            style={{ maxWidth: "100%", objectFit: "contain" }}
          />
        )}
      </div>
    </div>
  );
};

export default DocumentViewer;