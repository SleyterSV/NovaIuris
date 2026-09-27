"""Deterministic export contract. Rendering never invokes a model."""
from copy import deepcopy
from datetime import datetime, timezone
from ..utils.case_contract import normalize_case_result


def prepare_document(case_id, result, tool):
    if tool not in {'case', 'court'}:
        raise ValueError('Invalid document tool')
    if not isinstance(result, dict) or not result.get('success'):
        raise ValueError('A completed legal result is required')
    if not isinstance(case_id, str) or result.get('case_id') != case_id:
        raise ValueError('Case identity mismatch')
    if result.get('metadata', {}).get('case_id', case_id) != case_id:
        raise ValueError('Case metadata mismatch')
    data = normalize_case_result(result)
    sections = [
        ('Objeto de la consulta', data['case'] if 'case' in data else ''),
        ('Resumen', data['summary']),
        ('Antecedentes', data['analysis'].get('antecedentes', [])),
        ('Análisis jurídico', data['analysis']),
        ('Hechos relevantes', data['analysis'].get('facts', [])),
        ('Problemas jurídicos', data['analysis'].get('issues', [])),
        ('Marco normativo y jurisprudencial', data['research']),
        ('Argumentos', data['arguments']), ('Análisis probatorio', data['evidence']),
        ('Contraargumentos', data['counter_arguments']), ('Riesgos', data['risks']),
        ('Estrategia', data['strategy']), ('Informe y conclusiones', data['report']),
        ('Fuentes y citas', data['citations'])
    ]
    if tool == 'court':
        sections.extend([('Simulación', data.get('simulation', {})),
                         ('Información del grafo', data.get('graph', {}))])
    return deepcopy({
        'document_version': '1.0', 'case_id': case_id, 'tool': tool,
        'title': 'INFORME DE ANÁLISIS JURÍDICO' if tool == 'case' else 'INFORME DE SIMULACIÓN JURÍDICA',
        'prepared_at': datetime.now(timezone.utc).isoformat(),
        'sections': [{'title': title, 'content': value} for title, value in sections],
        'metadata': {'additional_ai_tokens': 0, 'renderer_status': 'pending_document_output'}
    })


class DocumentRenderer:
    """Future PDF/DOCX boundary; only already generated document data is accepted."""
    def render_pdf(self, document):
        raise NotImplementedError('PENDIENTE BLOQUE DOCUMENT OUTPUT')
