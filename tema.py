# tema.py
"""Paleta central do app, dependente do tema claro/escuro."""
import customtkinter as ctk


def _paleta_escura():
    return {
        "fundo":            "#0a1628",
        "fundo_frame":      "#0a1628",   # <- MESMA cor do fundo (linha some no fundo)
        "fundo_frame_hover":"#152a44",   # <- só no hover aparece a faixa
        "texto":            "#e6edf7",
        "texto_suave":      "#a4b3c9",
        "borda":            "#1c3050",

        "botao":            "#3B9EE5",
        "botao_hover":      "#2E7FC0",
        "botao_texto":      "#ffffff",

        "botao_neutro":     "#243a5c",
        "botao_neutro_hover":"#1c2f4a",

        "botao_editar":     "#3B9EE5",
        "botao_editar_hover":"#2E7FC0",

        "botao_perigo":     "#C0392B",
        "botao_perigo_hover":"#922B21",

        "entrada":          "#0f1e33",
        "entrada_borda":    "#1c3050",

        "aba_sel":          "#3B9EE5",
        "aba_sel_hover":    "#2E7FC0",
        "aba_unsel":        "#0f1e33",
        "aba_unsel_hover":  "#162a44",
    }


def _paleta_clara():
    return {
        "fundo":            "#eef2f7",
        "fundo_frame":      "#eef2f7",   # <- MESMA cor do fundo
        "fundo_frame_hover":"#dbe6f3",   # <- hover suave
        "texto":            "#1a2333",
        "texto_suave":      "#5a6b82",
        "borda":            "#c3cfe0",

        "botao":            "#3B9EE5",
        "botao_hover":      "#2E7FC0",
        "botao_texto":      "#ffffff",

        "botao_neutro":     "#d5dde8",
        "botao_neutro_hover":"#c0cad9",

        "botao_editar":     "#3B9EE5",
        "botao_editar_hover":"#2E7FC0",

        "botao_perigo":     "#C0392B",
        "botao_perigo_hover":"#922B21",

        "entrada":          "#ffffff",
        "entrada_borda":    "#c3cfe0",

        "aba_sel":          "#3B9EE5",
        "aba_sel_hover":    "#2E7FC0",
        "aba_unsel":        "#e2e8f2",
        "aba_unsel_hover":  "#d0dae8",
    }


def paleta():
    """Devolve o dict de cores do tema atualmente ativo."""
    if ctk.get_appearance_mode() == "Dark":
        return _paleta_escura()
    return _paleta_clara()