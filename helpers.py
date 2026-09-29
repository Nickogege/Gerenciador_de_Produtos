# helpers.py
TODAS = "Todas"



def ler_numero(texto, tipo):
    texto = texto.strip().replace(",", ".")
    return tipo(texto)


def formatar_preco(valor):
    return f"{valor:.2f}".replace(".", ",")


def centralizar_em(janela, pai, largura, altura):
    pai.update_idletasks()
    x = pai.winfo_x() + (pai.winfo_width() - largura) // 2
    y = pai.winfo_y() + (pai.winfo_height() - altura) // 2
    janela.geometry(f"{largura}x{altura}+{x}+{y}")


def capitalizar_nome(texto):
    return " ".join(palavra[:1].upper() + palavra[1:].lower() if palavra else ""
                    for palavra in texto.split(" "))


def validar_inteiro(texto):
    if texto == "":
        return True
    return texto.isdigit()


def validar_decimal(texto):
    if texto == "":
        return True
    if not all(c.isdigit() or c in ",." for c in texto):
        return False
    if texto.count(",") + texto.count(".") > 1:
        return False
    for sep in (",", "."):
        if sep in texto:
            parte_decimal = texto.split(sep, 1)[1]
            if len(parte_decimal) > 2:
                return False
    return True


def validar_texto_sem_numeros(texto):
    if texto == "":
        return True
    return not any(c.isdigit() for c in texto)