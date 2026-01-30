"""Script de exemplo para rodar o coletor de e-mails (IMAP).

Uso:
  - Preencha as variáveis IMAP_* no `.env` (veja `.env.example`)
  - No ambiente local: `python -m app.scripts.fetch_emails_sample`
  - No container: `docker-compose exec backend python -m app.scripts.fetch_emails_sample`

OBS: o coletor atual é um stub. Este script demonstra como invocar a função e onde colocar as credenciais.
"""
import os
from dotenv import load_dotenv

load_dotenv()

IMAP_HOST = os.environ.get('IMAP_HOST')
IMAP_USER = os.environ.get('IMAP_USER')
IMAP_PASS = os.environ.get('IMAP_PASS')
IMAP_FOLDER = os.environ.get('IMAP_FOLDER', 'INBOX')

OUTLOOK_TENANT_ID = os.environ.get('OUTLOOK_TENANT_ID')
OUTLOOK_CLIENT_ID = os.environ.get('OUTLOOK_CLIENT_ID')
OUTLOOK_CLIENT_SECRET = os.environ.get('OUTLOOK_CLIENT_SECRET')
OUTLOOK_USER = os.environ.get('OUTLOOK_USER')
OUTLOOK_FOLDER = os.environ.get('OUTLOOK_FOLDER', 'Inbox')

from app.services.email_collector import fetch_emails
from app.services.outlook_collector import fetch_outlook_emails


def main():
    # Prefer Outlook if configured
    if OUTLOOK_TENANT_ID and OUTLOOK_CLIENT_ID and OUTLOOK_CLIENT_SECRET and OUTLOOK_USER:
        print(f'Conectando via Microsoft Graph para {OUTLOOK_USER} (tenant {OUTLOOK_TENANT_ID})...')
        try:
            msgs = fetch_outlook_emails(OUTLOOK_TENANT_ID, OUTLOOK_CLIENT_ID, OUTLOOK_CLIENT_SECRET, OUTLOOK_USER, folder=OUTLOOK_FOLDER)
            print('fetch_outlook_emails retornou:', len(msgs), 'mensagens')
            for m in msgs[:5]:
                print('- ', m['message_id'], m['assunto'], 'attach:', len(m['attachments']))

            # If we have configuration for ingesting, run EmailIngestor
            from app.services.email_ingestor import EmailIngestor
            try:
                ingestor = EmailIngestor(OUTLOOK_TENANT_ID, OUTLOOK_CLIENT_ID, OUTLOOK_CLIENT_SECRET, OUTLOOK_USER, folder=OUTLOOK_FOLDER)
                docs = ingestor.ingest(top=20)
                print('Ingested', len(docs), 'document(s)')
            except Exception as e:
                print('Erro ao ingestar mensagens:', e)

        except Exception as e:
            print('Erro ao executar fetch_outlook_emails:', e)
        return

    # Fallback para IMAP
    if not (IMAP_HOST and IMAP_USER and IMAP_PASS):
        print('Faltando variáveis IMAP_* e OUTLOOK_*. Veja `.env.example` e preencha antes de executar.')
        return

    print(f'Conectando a IMAP {IMAP_HOST} como {IMAP_USER} (pasta {IMAP_FOLDER})...')
    # Chama o stub; implemente a persistência no coletor para produção
    try:
        result = fetch_emails(IMAP_HOST, IMAP_USER, IMAP_PASS, IMAP_FOLDER)
        print('fetch_emails retornou:', result)
    except Exception as e:
        print('Erro ao executar fetch_emails:', e)


if __name__ == '__main__':
    main()
