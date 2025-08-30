import { useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { SystemExplanation } from "@/components/system/SystemExplanation";
import { Button } from "@/components/ui/button";
import { MessageSquare, Info } from "lucide-react";

const Index = () => {
  const [activeView, setActiveView] = useState<"chat" | "explanation">("explanation");

  return (
    <AppLayout>
      <div className="h-full bg-background flex flex-col">
        <div className="border-b p-4 flex gap-2">
          <Button
            variant={activeView === "explanation" ? "default" : "outline"}
            onClick={() => setActiveView("explanation")}
            className="flex items-center gap-2"
          >
            <Info className="w-4 h-4" />
            Sobre o Sistema
          </Button>
          <Button
            variant={activeView === "chat" ? "default" : "outline"}
            onClick={() => setActiveView("chat")}
            className="flex items-center gap-2"
          >
            <MessageSquare className="w-4 h-4" />
            Chat Inteligente
          </Button>
        </div>
        
        <div className="flex-1 overflow-auto">
          {activeView === "explanation" ? (
            <SystemExplanation />
          ) : (
            <div className="h-full flex flex-col">
              <ChatContainer />
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};

export default Index;
