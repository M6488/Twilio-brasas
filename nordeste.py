def nordestinizar(texto: str) -> str:
    prefixo = "Oxente! "
    if texto.strip().lower().startswith("oxente"):
        return texto
    return f"{prefixo}{texto} 😊"