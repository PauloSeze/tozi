import os
from datetime import datetime, time
from zoneinfo import ZoneInfo

# --- Fuso horário ---
TZ = ZoneInfo("America/Cuiaba")

# --- Variáveis de ambiente ---
AMBIENTE = os.getenv("AMBIENTE", "desenvolvimento")
CONVERSA_TESTE_ID = int(os.getenv("CONVERSA_TESTE_ID", "0"))

SPX_BASE_URL = os.getenv("SPX_BASE_URL", "https://chat.simplexsolucoes.com.br")
SPX_ACCOUNT_ID = os.getenv("SPX_ACCOUNT_ID", "6")
SPX_BOT_TOKEN = os.getenv("SPX_BOT_TOKEN", "")
SPX_INBOX_ID = 91

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
VISTA_BASE_URL = os.getenv("VISTA_BASE_URL", "https://toz19328-rest.vistahost.com.br")
VISTA_API_KEY = os.getenv("VISTA_API_KEY", "")
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY", "")

# --- IDs fixos SPX ---
CAMILA_AGENT_ID = 66
TIME_LOCACAO_ID = 50
TIME_VENDAS_ID = 49
TIME_FINANCEIRO_ID = 56
TIME_MANUTENCAO_ID = 53

# --- Horário comercial Tozi ---
HORARIO_COMERCIAL = {
    0: [(time(7, 30), time(11, 30)), (time(13, 30), time(17, 30))],   # segunda
    1: [(time(7, 30), time(11, 30)), (time(13, 30), time(17, 30))],   # terça
    2: [(time(7, 30), time(11, 30)), (time(13, 30), time(17, 30))],   # quarta
    3: [(time(7, 30), time(11, 30)), (time(13, 30), time(17, 30))],   # quinta
    4: [(time(7, 30), time(11, 30)), (time(13, 30), time(17, 30))],   # sexta
    5: [(time(9, 0), time(11, 30))],                                   # sábado
    6: [],                                                              # domingo
}


def dentro_do_horario(agora: datetime | None = None) -> bool:
    if agora is None:
        agora = datetime.now(TZ)
    faixas = HORARIO_COMERCIAL.get(agora.weekday(), [])
    hora_atual = agora.time()
    return any(inicio <= hora_atual <= fim for inicio, fim in faixas)


def deve_processar(conversa_id: int) -> bool:
    if AMBIENTE == "producao":
        return True
    if CONVERSA_TESTE_ID == 0:
        return True  # dev sem filtro — processa tudo
    return conversa_id == CONVERSA_TESTE_ID
