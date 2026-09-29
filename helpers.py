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


def capitalizar_nome(texto):
    """Coloca a primeira letra de cada palavra em maiúscula."""
    return " ".join(palavra[:1].upper() + palavra[1:].lower() if palavra else ""
                    for palavra in texto.split(" "))


def validar_inteiro(texto):
    """Permite apenas dígitos (string vazia é permitida)."""
    if texto == "":
        return True
    return texto.isdigit()


def validar_decimal(texto):
    """Permite dígitos, uma vírgula ou ponto, e até 2 casas decimais."""
    if texto == "":
        return True
    # aceita apenas dígitos, vírgula e ponto
    if not all(c.isdigit() or c in ",." for c in texto):
        return False
    # no máximo um separador decimal
    if texto.count(",") + texto.count(".") > 1:
        return False
    # no máximo 2 casas após o separador
    for sep in (",", "."):
        if sep in texto:
            parte_decimal = texto.split(sep, 1)[1]
            if len(parte_decimal) > 2:
                return False
    return True


def validar_texto_sem_numeros(texto):
    """Permite apenas letras, espaços e acentos (sem números)."""
    if texto == "":
        return True
    return not any(c.isdigit() for c in texto)