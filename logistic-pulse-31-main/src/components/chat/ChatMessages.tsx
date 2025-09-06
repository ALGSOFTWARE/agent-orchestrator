import { useEffect, useRef } from "react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { Bot, User, Download, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import { Message } from "./ChatContainer";
import { Button } from "@/components/ui/button";
import { TypingIndicator } from "./TypingIndicator";

interface ChatMessagesProps {
  messages: Message[];
}

const getDocumentIcon = (type: string) => {
  switch (type) {
    case "CTE":
      return "🚛";
    case "AWL":
      return "✈️";
    case "BL":
      return "🚢";
    case "MANIFESTO":
      return "📋";
    case "NF":
      return "🧾";
    default:
      return "📄";
  }
};

export const ChatMessages = ({ messages }: ChatMessagesProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={cn(
            "flex",
            message.type === "user" ? "justify-end" : "justify-start"
          )}
        >
          <div
            className={cn(
              "max-w-[70%] rounded-lg p-3 shadow-soft",
              message.type === "user"
                ? "bg-gradient-primary text-brand-dark"
                : message.type === "agent"
                ? "bg-card border border-border"
                : "bg-muted"
            )}
          >
            <div className="flex items-start space-x-3">
              {message.type !== "user" && (
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center mt-1",
                  message.type === "agent" ? "bg-brand-primary" : "bg-muted-foreground"
                )}>
                  {message.type === "agent" ? (
                    <Bot className="w-4 h-4 text-brand-dark" />
                  ) : (
                    <FileText className="w-4 h-4 text-white" />
                  )}
                </div>
              )}
              
              <div className="flex-1">
                {message.isLoading ? (
                  <div className="flex items-center space-x-3">
                    <span className="text-sm text-muted-foreground italic">
                      {message.content}
                    </span>
                    <TypingIndicator />
                  </div>
                ) : (
                  <p className={cn(
                    "text-sm",
                    message.type === "user" 
                      ? "text-brand-dark" 
                      : "text-foreground"
                  )}>
                    {message.content}
                  </p>
                )}
                
                {message.attachments && message.attachments.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {message.attachments.map((attachment, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-2 bg-muted rounded-lg border"
                      >
                        <div className="flex items-center space-x-2">
                          <span className="text-lg">{getDocumentIcon(attachment.type)}</span>
                          <div>
                            <p className="text-xs font-medium text-foreground">
                              {attachment.name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {attachment.type}
                            </p>
                          </div>
                        </div>
                        
                        <Button size="sm" variant="ghost">
                          <Download className="w-3 h-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
                
                <p className={cn(
                  "text-xs mt-2",
                  message.type === "user" 
                    ? "text-brand-dark/70" 
                    : "text-muted-foreground"
                )}>
                  {format(message.timestamp, "HH:mm", { locale: ptBR })}
                </p>
              </div>
              
              {message.type === "user" && (
                <div className="w-8 h-8 bg-brand-dark rounded-full flex items-center justify-center mt-1">
                  <User className="w-4 h-4 text-brand-primary" />
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};