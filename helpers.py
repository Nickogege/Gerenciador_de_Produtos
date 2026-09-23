TODAS = "Todas"  


def ler_numero(texto, tipo):
    """Converte texto em int/float aceitando vírgula decimal (ex: 10,50)."""
    texto = texto.strip().replace(",", ".")
    return tipo(texto)


def formatar_preco(valor):
    """Formata o preço no padrão brasileiro: 1234.5 -> 1234,50"""
    return f"{valor:.2f}".replace(".", ",")


def centralizar_em(janela, pai, largura, altura):
    """Posiciona 'janela' no centro da janela 'pai'."""
    pai.update_idletasks()
    x = pai.winfo_x() + (pai.winfo_width() - largura) // 2
    y = pai.winfo_y() + (pai.winfo_height() - altura) // 2
    janela.geometry(f"{largura}x{altura}+{x}+{y}")
