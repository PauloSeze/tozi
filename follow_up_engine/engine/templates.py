"""Templates de mensagem inicial para prospecção ativa (SDR Passivo)."""
from __future__ import annotations

from string import Template

# Mapeamento de fonte → template inicial (1ª pessoa do plural, picado, sem promessa)
TEMPLATES: dict[str, str] = {
    "META_ADS": "Oi $first_name, tudo bem? Aqui é da Tozi Imóveis. Vi que você se interessou pelo anúncio que rolou no Facebook/Instagram. A gente tá por aqui pra te ajudar a achar o imóvel certo. Me conta um pouco do que você tá procurando?",
    "SITE": "Oi $first_name! Aqui é da Tozi Imóveis, vi que você fez contato pelo nosso site. A gente cuida de locação e venda em Sinop. Conta pra mim o que você tá procurando que já te ajudo.",
    "INSTAGRAM": "Oi $first_name! Tozi Imóveis por aqui. Vi que você curtiu nosso conteúdo no Instagram. Posso ajudar a achar um imóvel pra você?",
    "FORMS_FINANCIAMENTO": "Oi $first_name, tudo bem? Aqui é da Tozi, vi seu interesse em financiamento. A gente trabalha com várias opções de imóvel pra quem quer comprar com financiamento bancário ou MCMV. Me conta o que você tem em mente?",
    "CHATBOT": "Oi $first_name! Aqui é da Tozi Imóveis. Notei que você começou uma conversa mas a gente não fechou o assunto. Posso continuar te ajudando agora?",
    "DEFAULT": "Oi $first_name, tudo bem? Aqui é da Tozi Imóveis de Sinop. A gente cuida de locação e venda. Como posso te ajudar?",
}

# Templates de follow-up por dia desde o último contato sem resposta
FOLLOWUP_TEMPLATES: dict[int, str] = {
    1: "Oi $first_name, é da Tozi de novo. Conseguiu pensar sobre o que a gente conversou ontem? Tô por aqui se quiser continuar.",
    3: "Oi $first_name! Passando pra saber se você ainda tá interessado. Se mudou de ideia tudo bem, é só me dizer. Ou se tem alguma dúvida, manda aí.",
    7: "Oi $first_name, tudo bem? A gente conversou faz uma semana e queria saber se ainda faz sentido continuar. Posso te mostrar alguma opção nova?",
    14: "Oi $first_name! Semana passada apareceram umas opções novas que podem combinar com o que você procurava. Quer que eu te mostre?",
    30: "Oi $first_name, tudo bem? Um mês passou rápido. Se ainda tá no radar achar um imóvel, a gente segue por aqui. Manda um sinal.",
    60: "Oi $first_name! Faz uns 2 meses que a gente não conversa. Tá tudo bem? Se ainda procura imóvel, posso te atualizar com o que tem agora.",
    90: "Oi $first_name, é da Tozi. Já faz 3 meses do nosso último papo. Vou parar de te chamar pra não incomodar, mas se um dia precisar é só voltar aqui.",
}


def first_name_of(full_name: str) -> str:
    parts = (full_name or "").strip().split()
    return parts[0].title() if parts else "tudo bem"


def render_initial(source: str | None, full_name: str) -> str:
    key = (source or "DEFAULT").upper().replace(" ", "_").replace("|", "_").replace("-", "_")
    # Normalização das fontes reais do Vista
    if "META" in key or "FACEBOOK" in key:
        key = "META_ADS"
    elif "SITE" in key:
        key = "SITE"
    elif "INSTAGRAM" in key:
        key = "INSTAGRAM"
    elif "FORM" in key and "FINANC" in key:
        key = "FORMS_FINANCIAMENTO"
    elif "CHATBOT" in key:
        key = "CHATBOT"
    else:
        key = "DEFAULT"
    template = Template(TEMPLATES[key])
    return template.substitute(first_name=first_name_of(full_name))


def render_followup(days_since: int, full_name: str) -> str | None:
    if days_since not in FOLLOWUP_TEMPLATES:
        return None
    template = Template(FOLLOWUP_TEMPLATES[days_since])
    return template.substitute(first_name=first_name_of(full_name))
