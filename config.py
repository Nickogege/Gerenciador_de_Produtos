# config.py
"""Preferências persistentes do app (tema, etc.)."""
import json
import os

CAMINHO = "config.json"

_PADRAO = {
    "tema": "dark",  # "dark" | "light"
}


def carregar():
    if not os.path.exists(CAMINHO):
        return dict(_PADRAO)
    try:
        with open(CAMINHO, "r", encoding="utf-8") as f:
            dados = json.load(f)
        # garante chaves faltantes
        for k, v in _PADRAO.items():
            dados.setdefault(k, v)
        return dados
    except (json.JSONDecodeError, OSError):
        return dict(_PADRAO)


def salvar(cfg):
    try:
        with open(CAMINHO, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except OSError:
        pass