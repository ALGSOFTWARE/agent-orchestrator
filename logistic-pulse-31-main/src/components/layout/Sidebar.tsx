import { 
  BarChart3, 
  Route, 
  Truck, 
  Users, 
  FileText, 
  TrendingUp, 
  MessageCircle, 
  Settings,
  Activity,
  LogOut,
  User,
  ChevronDown
} from "lucide-react";
import { cn } from "@/lib/utils";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useState } from "react";

const getCurrentPath = () => window.location.pathname;

const navigation = [
  { name: "Dashboard", icon: BarChart3, href: "/dashboard", current: false },
  { name: "Jornadas", icon: Route, href: "/jornadas", current: false },
  { name: "Entregas", icon: Truck, href: "/entregas", current: false },
  { name: "Clientes", icon: Users, href: "/clientes", current: false },
  { name: "Documentos", icon: FileText, href: "/documentos", current: false },
  { name: "Relatórios", icon: TrendingUp, href: "/relatorios", current: false },
  { name: "Chat", icon: MessageCircle, href: "/chat", current: false },
  { name: "Configurações", icon: Settings, href: "/configuracoes", current: false },
];

const getNavigationWithCurrent = () => {
  const currentPath = getCurrentPath();
  return navigation.map(item => ({
    ...item,
    current: item.href === currentPath || (currentPath === "/" && item.href === "/")
  }));
};

export const Sidebar = () => {
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const handleLogout = () => {
    // Implementar lógica de logout aqui
    console.log("Fazendo logout...");
    window.location.href = "/login";
  };

  const handleProfile = () => {
    // Implementar navegação para perfil
    console.log("Abrindo perfil...");
    window.location.href = "/configuracoes";
  };

  return (
    <div className="w-64 h-full bg-sidebar-bg text-sidebar-text flex flex-col border-r border-sidebar-hover">
      {/* Logo */}
      <div className="p-6 border-b border-sidebar-hover">
        <div className="flex justify-center">
          <div className="w-16 h-16 rounded-lg overflow-hidden">
            <img 
              src="/lovable-uploads/mit logo branco.png" 
              alt="MIT Logo" 
              className="w-full h-full object-cover"
            />
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {getNavigationWithCurrent().map((item) => (
            <li key={item.name}>
              <a
                href={item.href}
                className={cn(
                  "flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  item.current
                    ? "bg-brand-primary text-brand-dark shadow-soft"
                    : "text-sidebar-text-muted hover:bg-sidebar-hover hover:text-sidebar-text"
                )}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      {/* User Profile with Dropdown */}
      <div className="p-4 border-t border-sidebar-hover">
        <DropdownMenu open={isProfileOpen} onOpenChange={setIsProfileOpen}>
          <DropdownMenuTrigger asChild>
            <button className="w-full flex items-center space-x-3 p-2 rounded-lg hover:bg-sidebar-hover transition-colors duration-200">
              <div className="w-8 h-8 bg-brand-primary rounded-full flex items-center justify-center">
                <span className="text-xs font-bold text-brand-dark">JS</span>
              </div>
              <div className="flex-1 min-w-0 text-left">
                <p className="text-sm font-medium text-sidebar-text truncate">João Silva</p>
                <p className="text-xs text-sidebar-text-muted truncate">Operador Logístico</p>
              </div>
              <ChevronDown className={cn(
                "w-4 h-4 text-sidebar-text-muted transition-transform duration-200",
                isProfileOpen && "rotate-180"
              )} />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent 
            align="end" 
            className="w-56 mb-2"
            side="top"
          >
            <DropdownMenuItem onClick={handleProfile} className="cursor-pointer">
              <User className="w-4 h-4 mr-2" />
              Gerenciar Perfil
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => window.location.href = "/configuracoes"} className="cursor-pointer">
              <Settings className="w-4 h-4 mr-2" />
              Configurações
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem 
              onClick={handleLogout}
              className="cursor-pointer text-destructive focus:text-destructive focus:bg-destructive/10"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sair
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
};