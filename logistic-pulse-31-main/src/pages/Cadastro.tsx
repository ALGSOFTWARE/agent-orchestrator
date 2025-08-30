import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";

export default function Cadastro() {
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");
  const [perfil, setPerfil] = useState("cliente");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleCadastro = async () => {
    if (!nome || !email || !senha || !confirmarSenha) {
      toast.error("Preencha todos os campos!");
      return;
    }
    if (senha !== confirmarSenha) {
      toast.error("As senhas não conferem!");
      return;
    }
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      toast.success("Cadastro realizado com sucesso! Seja bem-vindo ao Stagg Tracking.");
      navigate("/login");
    }, 1500);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-900 via-green-950 to-black">
      <Card className="w-full max-w-lg shadow-2xl animate-fade-in">
        <CardHeader className="flex flex-col items-center gap-2">
          <img src="/lovable-uploads/014d0582-1936-4d59-8f55-b3f16bdb41b3.png" alt="Logo Stagg" className="w-20 h-20 mb-2 animate-bounce" />
          <CardTitle className="text-3xl font-bold text-green-600">Crie sua conta</CardTitle>
          <span className="text-muted-foreground text-center">Bem-vindo ao futuro da logística inteligente!<br/>Preencha seus dados para começar.</span>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="nome">Nome completo</Label>
            <Input id="nome" value={nome} onChange={e => setNome(e.target.value)} placeholder="Seu nome" autoFocus required />
          </div>
          <div>
            <Label htmlFor="email">E-mail</Label>
            <Input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="seu@email.com" required />
          </div>
          <div className="flex gap-2">
            <div className="flex-1">
              <Label htmlFor="senha">Senha</Label>
              <Input id="senha" type="password" value={senha} onChange={e => setSenha(e.target.value)} placeholder="********" required />
            </div>
            <div className="flex-1">
              <Label htmlFor="confirmarSenha">Confirmar Senha</Label>
              <Input id="confirmarSenha" type="password" value={confirmarSenha} onChange={e => setConfirmarSenha(e.target.value)} placeholder="********" required />
            </div>
          </div>
          <div>
            <Label htmlFor="perfil">Perfil</Label>
            <Select value={perfil} onValueChange={setPerfil}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Selecione o perfil" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="cliente">Cliente</SelectItem>
                <SelectItem value="funcionario">Funcionário</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button onClick={handleCadastro} className="w-full mt-2" disabled={loading}>
            {loading ? "Cadastrando..." : "Cadastrar"}
          </Button>
          <div className="text-center text-sm mt-2">
            Já tem uma conta? <a href="/login" className="text-green-600 hover:underline">Entrar</a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}