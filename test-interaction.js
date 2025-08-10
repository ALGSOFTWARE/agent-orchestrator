import { spawn } from 'child_process';

console.log('🧪 Testando MIT Tracking Agent Interativo...\n');

const agente = spawn('node', ['interactive-agent.js'], {
  stdio: ['pipe', 'pipe', 'pipe']
});

// Aguarda inicialização
setTimeout(() => {
  console.log('📝 Enviando pergunta de teste...');
  agente.stdin.write('Como consultar um CT-e no sistema MIT Tracking?\n');
  
  setTimeout(() => {
    console.log('\n📝 Enviando comando de saída...');
    agente.stdin.write('/sair\n');
  }, 8000);
}, 3000);

agente.stdout.on('data', (data) => {
  console.log(data.toString());
});

agente.stderr.on('data', (data) => {
  console.error(`Erro: ${data}`);
});

agente.on('close', (code) => {
  console.log(`\n✅ Teste concluído! Código de saída: ${code}`);
});

// Timeout de segurança
setTimeout(() => {
  agente.kill();
  console.log('\n⏰ Teste encerrado por timeout.');
}, 15000);