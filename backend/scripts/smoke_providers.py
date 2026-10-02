"""Explicit, minimal provider smoke. Never runs external calls by default."""
import argparse
import os
import time
from urllib.request import Request, urlopen


def plan():
    return {
        'supabase': (('SUPABASE_URL', 'SUPABASE_PUBLISHABLE_KEY'), 'GET /rest/v1/ (connectivity)'),
        'openai_generation': (('LLM_API_KEY', 'LLM_MODEL_NAME'), 'one synthetic, minimal chat generation'),
        'openai_embedding': (('OPENAI_API_KEY',), 'one synthetic embedding'),
        'zep': (('ZEP_API_KEY',), 'one SDK health/read operation'),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    for provider, (variables, operation) in plan().items():
        missing = [name for name in variables if not os.getenv(name)]
        print(f'{provider}: {operation}; requires={",".join(variables)}; configured={not missing}')
    if args.dry_run:
        print('DRY_RUN: no provider calls')
        return 0
    if os.getenv('RUN_PROVIDER_SMOKE') != '1' or os.getenv('APP_ENV') != 'production':
        print('RUNTIME_PROVIDER_VALIDATION_PENDING: set RUN_PROVIDER_SMOKE=1 and APP_ENV=production')
        return 2
    if any(not all(os.getenv(name) for name in variables) for variables, _ in plan().values()):
        print('RUNTIME_PROVIDER_VALIDATION_PENDING: required provider configuration missing')
        return 2
    from openai import OpenAI
    from zep_cloud.client import Zep
    client = OpenAI(api_key=os.environ['LLM_API_KEY'],
                    base_url=os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1'),
                    timeout=15, max_retries=0)
    embedding_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], timeout=15, max_retries=0)
    checks = [
        ('supabase', lambda: urlopen(Request(os.environ['SUPABASE_URL'].rstrip('/') + '/rest/v1/',
            headers={'apikey': os.environ['SUPABASE_PUBLISHABLE_KEY']}), timeout=10).close()),
        ('openai_generation', lambda: client.chat.completions.create(model=os.environ['LLM_MODEL_NAME'],
            messages=[{'role': 'user', 'content': 'Responde: OK'}], max_tokens=4)),
        ('openai_embedding', lambda: embedding_client.embeddings.create(model=os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small'),
            input='prueba sintética')),
        ('zep', lambda: Zep(api_key=os.environ['ZEP_API_KEY']).graph.list_all(page_size=1)),
    ]
    failed = False
    for name, operation in checks:
        started = time.monotonic()
        try:
            operation()
            status = 'passed'
        except Exception as error:
            status = 'failed:' + type(error).__name__
            failed = True
        print(f'{name}: {status}; duration_ms={round((time.monotonic()-started)*1000)}')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
