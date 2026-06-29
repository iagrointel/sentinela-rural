"""WhatsApp — envio via Meta Cloud API + fluxo de conversa de referência.

Este é o método (a tradução em linguagem rural — o gargalo nomeado pelo MGI), NÃO a operação.
A chave da Meta é SUA (lida de variável de ambiente). O webhook de produção, a fila concorrente
e a integração com a base nacional ficam fora deste repositório — são o serviço da equipe.
"""
import os
import requests

GRAPH = "https://graph.facebook.com/v20.0"


def _cfg():
    token = os.environ.get("META_TOKEN")
    phone_id = os.environ.get("META_PHONE_NUMBER_ID")
    if not token or not phone_id:
        raise RuntimeError("Defina META_TOKEN e META_PHONE_NUMBER_ID no .env (use .env.example).")
    return token, phone_id


def send_text(to: str, body: str):
    """Envia uma mensagem de texto pelo WhatsApp (Meta Cloud API)."""
    token, phone_id = _cfg()
    r = requests.post(
        f"{GRAPH}/{phone_id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


# --- Fluxo de conversa de referência: a tradução em linguagem rural (o que / como / até quando) ---

def msg_clima(nome: str) -> str:
    # A retenção que mantém o canal vivo — o motivo de ele abrir a mensagem do CAR.
    return (f"☀️ Bom dia, {nome}! Hoje sol, sem chuva — boa janela pra pulverizar. "
            f"Amanhã pancada à tarde. (previsão do seu sítio)")


def msg_app(nome: str, app_ha: float) -> str:
    return (f"Olá, {nome}! Aqui é o órgão ambiental, pelo Sentinela Rural. O córrego que corta sua terra "
            f"precisa de uma faixa de mata (a lei chama de APP) de ~{app_ha} ha que ainda não está no seu CAR.\n"
            f"✅ O que fazer: marcar essa faixa — eu já desenhei pra você.\n"
            f"📅 Até o prazo do PRA do seu estado.\n"
            f"Posso te mostrar no satélite, aqui pelo WhatsApp?")


def msg_reserva_legal(nome: str, deficit_pct: float) -> str:
    return (f"Olá, {nome}! Seu imóvel está com a Reserva Legal abaixo do mínimo (faltam ~{deficit_pct}%). "
            f"Dá pra resolver pelo WhatsApp, sem técnico. Quer que eu te mostre o que falta?")


def msg_pacote() -> str:
    return ("📎 Pronto: CAR_retificacao.kml + dossiê. É só importar no módulo oficial e enviar no SICAR — "
            "te guio passo a passo. O aceite é seu, lá no SICAR.")


def fluxo_referencia(nome: str, diag: dict) -> list[str]:
    """Sequência de mensagens (o que o produtor recebe). Retorna a lista, sem enviar."""
    seq = [msg_clima(nome)]
    if diag.get("app_omitida_ha", 0) > 0:
        seq.append(msg_app(nome, diag["app_omitida_ha"]))
    if diag.get("reserva_legal", {}).get("deficit_pct", 0) > 0:
        seq.append(msg_reserva_legal(nome, diag["reserva_legal"]["deficit_pct"]))
    seq.append(msg_pacote())
    return seq
