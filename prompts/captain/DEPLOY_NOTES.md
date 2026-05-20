# Deploy Notes — Custom Tools Tozi

## Estado atual

| Componente | Estado |
|---|---|
| Fix `safe_endpoint_validatable.rb` | ✅ Aplicado no working tree do chatspx local, **sem commit** |
| Push pra GitHub (branch `paulao`) | ⏳ Você decide |
| Deploy em `paulo.chatspx.app` | ⏳ Manual (Proxmox), não está no Coolify |
| Payloads das 2 Custom Tools | ✅ Em `_payloads/` |
| Script de apply | ✅ `apply_custom_tools.py` |

## Fix do validator (1 linha)

```
chatspx/enterprise/app/models/concerns/safe_endpoint_validatable.rb
- sanitized_url = endpoint_url.gsub(/\{\{[^}]+\}\}/, 'placeholder')
+ sanitized_url = endpoint_url.gsub(/\{\{[^}]+\}\}|\{%[^%]+%\}/, 'placeholder')
```

Verificar com:
```bash
git -C C:/Users/paulo/Workspaces/chatspx diff enterprise/app/models/concerns/safe_endpoint_validatable.rb
```

## Caminho de deploy sugerido

1. **Revisar o diff** — `git diff` no chatspx mostra a alteração
2. **Spec opcional** — escrever um spec rápido em `chatspx/spec/enterprise/models/concerns/safe_endpoint_validatable_spec.rb` cobrindo:
   - URL com `{% if x %},..{% endif %}` deve validar como válida
   - URL com `{{ var }}` continua validando como válida (regressão)
3. **Commit** na branch `paulao`:
   ```bash
   git -C C:/Users/paulo/Workspaces/chatspx add enterprise/app/models/concerns/safe_endpoint_validatable.rb
   git -C C:/Users/paulo/Workspaces/chatspx commit -m "fix(captain): aceitar tags Liquid {% %} no endpoint_url do CustomTool"
   ```
4. **Push** — `git push origin paulao`
5. **Deploy em paulo.chatspx.app** — segue o procedimento Proxmox que você já usa. Provavelmente pull + bundle install (se mudar gem, mas não muda) + restart rails.

⚠️ **Não rodar `systemctl restart` em produção sem `rails db:migrate:status` antes** — regra do AGENTS.md do chatspx (incidente de 24-abr-2026 documentado lá).

## Depois do deploy

Roda:
```bash
cd C:/Users/paulo/Workspaces/tozi/prompts/captain
python apply_custom_tools.py --dry-run    # mostra o que faria
python apply_custom_tools.py              # aplica de verdade
```

O script:
1. Cria/atualiza `buscar_imoveis_vista` (Vista CRM)
2. Cria/atualiza `buscar_localizacao` (Google Maps + bbox 3km)
3. Vincula as 2 tools aos Scenarios `Vendas` e `Locação` (Suporte fica sem — só usa `faq_lookup` nativo)

## Como testar depois

Manda WhatsApp pro número da Inbox 1:

- "Quero alugar uma casa de 3 quartos no Jardim Ouro até 2 mil" — Bruna usa `buscar_imoveis_vista(status_tipo=locacao, bairro=Jardim Ouro, dormitorios=3, valor_max=2000)`
- "Tem imóvel pra alugar perto da Unifasipe?" — Bruna usa `buscar_localizacao(local=Unifasipe)` → pega lat/lng → `buscar_imoveis_vista(latitude_min=..., latitude_max=..., longitude_min=..., longitude_max=...)`
- "Quero comprar terreno em Sinop até 300 mil" — Júlia usa `buscar_imoveis_vista(status_tipo=venda, categoria=Terreno, valor_max=300000)`

Tracing em `https://paulo.chatspx.app/app/accounts/1/agents/1/logs` (AssistantLog).
