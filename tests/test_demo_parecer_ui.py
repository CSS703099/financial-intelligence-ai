"""Testes de governança da interface offline — sem chamadas de API."""
import pytest

from scripts.demo_parecer_offline import montar_demo
from scripts.demo_parecer_ui import ORIGEM, construir_exportacao


@pytest.mark.parametrize('tipo', ['credito', 'repasses'])
def test_exportacao_manual_rotulada_e_assinada(tipo):
    dossie, parecer = montar_demo(tipo)
    pacote = construir_exportacao(dossie, parecer, 'Revisor de teste')
    assert pacote['origem_parecer'] == ORIGEM
    assert pacote['status'] == 'APROVADO_POR_HUMANO'
    assert pacote['aprovador'] == 'Revisor de teste'
    assert len(pacote['dossie_sha256']) == 64
    assert pacote['uso_permitido'] == 'DEMONSTRACAO_LOCAL_COM_DADOS_SINTETICOS'


def test_exportacao_sem_revisor_rejeitada():
    dossie, parecer = montar_demo('credito')
    with pytest.raises(ValueError):
        construir_exportacao(dossie, parecer, '   ')


def test_exportacao_evidencia_inventada_rejeitada():
    dossie, parecer = montar_demo('credito')
    parecer['evidencias_ids'].append('X999')
    with pytest.raises(ValueError):
        construir_exportacao(dossie, parecer, 'Revisor de teste')
