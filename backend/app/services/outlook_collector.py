"""Coletor para Outlook usando Microsoft Graph (client credentials / app permissions).

MVP behavior:
- Usa OAuth2 client_credentials para obter token (app registra no Azure AD)
- Lê mensagens de `/users/{user_email}/mailFolders/{folder}/messages`
- Busca metadados: id, subject, from, bodyPreview, receivedDateTime, webLink
- Baixa attachments (fileAttachment) e salva no STORAGE_DIR
- Retorna lista de mensagens com anexos resumidos

Notas de segurança/produção:
- Para acessar caixas de outros usuários é necessário conceder permissão Application (Mail.Read)
- Para acessar a caixa do próprio usuário via delegated flow, use OAuth2 código/Device flow
- Este módulo é um MVP: adicionar paginação, delta sync, retries e tratamento de erros
"""
import os
import base64
import requests
from typing import List

TOKEN_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

STORAGE_DIR = os.environ.get('STORAGE_DIR', '/data/storage')
os.makedirs(STORAGE_DIR, exist_ok=True)


def _get_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    url = TOKEN_URL.format(tenant_id=tenant_id)
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    r = requests.post(url, data=data, timeout=10)
    r.raise_for_status()
    return r.json()['access_token']


def _save_attachment_bytes(user: str, message_id: str, filename: str, content_bytes: bytes) -> str:
    user_dir = os.path.join(STORAGE_DIR, user.replace('@', '_'))
    os.makedirs(user_dir, exist_ok=True)
    safe_name = f"{message_id}_{filename}"
    path = os.path.join(user_dir, safe_name)
    with open(path, 'wb') as f:
        f.write(content_bytes)
    return path


def _fetch_attachments(token: str, user: str, message_id: str) -> List[dict]:
    url = f"{GRAPH_BASE}/users/{user}/messages/{message_id}/attachments"
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    out = []
    for item in r.json().get('value', []):
        # fileAttachment case
        if item.get('@odata.type') == '#microsoft.graph.fileAttachment' or item.get('contentBytes'):
            filename = item.get('name') or 'attachment'
            content_bytes = base64.b64decode(item.get('contentBytes') or '')
            path = _save_attachment_bytes(user, message_id, filename, content_bytes)
            out.append({'nome_arquivo': filename, 'caminho_arquivo': path})
        else:
            # other types (reference, itemAttachment) - store metadata only
            out.append({'nome_arquivo': item.get('name') or 'attachment', 'caminho_arquivo': None})
    return out


def fetch_outlook_emails(tenant_id: str, client_id: str, client_secret: str, user_email: str, folder: str = 'Inbox', top: int = 20) -> List[dict]:
    """Fetch latest messages from a user mailbox.

    Returns list of dicts: {message_id, remetente, assunto, corpo_preview, data_hora_email, webLink, attachments: [...]}
    """
    token = _get_token(tenant_id, client_id, client_secret)
    # select fields we need
    select = 'id,subject,from,bodyPreview,receivedDateTime,webLink'
    url = f"{GRAPH_BASE}/users/{user_email}/mailFolders/{folder}/messages?$select={select}&$top={top}"
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()

    messages = []
    for m in r.json().get('value', []):
        message_id = m.get('id')
        remetente = (m.get('from') or {}).get('emailAddress', {}).get('address')
        assunto = m.get('subject')
        corpo_preview = m.get('bodyPreview')
        data_hora_email = m.get('receivedDateTime')
        webLink = m.get('webLink')

        attachments = _fetch_attachments(token, user_email, message_id)

        messages.append({
            'message_id': message_id,
            'remetente': remetente,
            'assunto': assunto,
            'corpo_preview': corpo_preview,
            'data_hora_email': data_hora_email,
            'webLink': webLink,
            'attachments': attachments,
        })

    return messages
