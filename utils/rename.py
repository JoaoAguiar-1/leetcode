from pathlib import Path
import re
import unicodedata


def remover_acentos(texto: str) -> str:
    """Remove acentos de uma string."""
    return ''.join(
        caractere
        for caractere in unicodedata.normalize('NFKD', texto)
        if not unicodedata.combining(caractere)
    )


def gerar_novo_nome(nome: str) -> str:
    """
    Aplica a regra de normalização ao nome do arquivo.

    Exemplos:
        "Meu Arquivo.txt"       -> "meu-arquivo.txt"
        "Relatório Final.PDF"   -> "relatorio-final.pdf"
        "Arquivo  Teste.txt"    -> "arquivo-teste.txt"
    """
    arquivo = Path(nome)

    # Separa nome e extensão para preservar o ponto da extensão.
    nome_base = arquivo.stem
    extensao = arquivo.suffix.lower()

    # Normaliza acentos.
    nome_base = remover_acentos(nome_base)

    # Converte para minúsculas e remove espaços nas extremidades.
    nome_base = nome_base.lower().strip()

    # Qualquer sequência de caracteres que não seja letra/número
    # vira um único hífen.
    nome_base = re.sub(r'[^a-z0-9]+', '-', nome_base)

    # Remove hífens das extremidades.
    nome_base = nome_base.strip('-')

    return f"{nome_base}{extensao}"


def gerar_nome_disponivel(caminho: Path) -> Path:
    """
    Caso o nome já exista, cria um nome alternativo.

    Exemplo:
        arquivo.txt
        arquivo-1.txt
        arquivo-2.txt
    """
    contador = 1

    while True:
        novo_nome = (
            caminho.parent
            / f"{caminho.stem}-{contador}{caminho.suffix}"
        )

        if not novo_nome.exists():
            return novo_nome

        contador += 1


def renomear_arquivo(
    caminho: Path,
    sobrescrever: bool = False
) -> Path:
    """
    Renomeia um arquivo aplicando a regra definida.

    Args:
        caminho: Caminho do arquivo original.
        sobrescrever: Se True, permite substituir um arquivo existente.
                       Se False, cria um nome alternativo.

    Returns:
        Caminho final do arquivo.
    """
    novo_nome = gerar_novo_nome(caminho.name)
    destino = caminho.parent / novo_nome

    # Não há necessidade de renomear.
    if caminho == destino:
        return caminho

    # O destino já existe.
    if destino.exists():

        if sobrescrever:
            caminho.replace(destino)
            return destino

        destino = gerar_nome_disponivel(destino)

    caminho.rename(destino)

    return destino


def renomear_arquivos(
    pasta: str | Path,
    sobrescrever: bool = False
) -> None:
    """
    Percorre a pasta e todas as suas subpastas, renomeando os arquivos.

    Args:
        pasta: Pasta raiz onde a busca será iniciada.
        sobrescrever: Define se arquivos existentes podem ser substituídos.
    """
    pasta = Path(pasta)

    if not pasta.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {pasta}")

    if not pasta.is_dir():
        raise NotADirectoryError(f"O caminho não é uma pasta: {pasta}")

    # rglob("*") percorre a pasta e todas as subpastas.
    for caminho in pasta.rglob("*"):

        # Ignora diretórios.
        if not caminho.is_file():
            continue

        try:
            novo_caminho = renomear_arquivo(
                caminho,
                sobrescrever=sobrescrever
            )

            if novo_caminho != caminho:
                print(f"Renomeado: {caminho} -> {novo_caminho}")

        except Exception as erro:
            print(f"Erro ao renomear {caminho}: {erro}")


if __name__ == "__main__":
    renomear_arquivos(
        pasta="./quests",
        sobrescrever=False
    )