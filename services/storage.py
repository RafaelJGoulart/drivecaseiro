import os
import shutil

UPLOAD_FOLDER = "uploads"


def tamanho_uploads():

    tamanho = 0

    for pasta, _, arquivos in os.walk(UPLOAD_FOLDER):

        for arquivo in arquivos:

            caminho = os.path.join(pasta, arquivo)

            if os.path.isfile(caminho):
                tamanho += os.path.getsize(caminho)

    return tamanho


def disco():

    total, usado, livre = shutil.disk_usage(".")

    return {
        "total": total,
        "usado": usado,
        "livre": livre
    }


def formatar(bytes):

    unidades = ["B", "KB", "MB", "GB", "TB"]

    tamanho = float(bytes)

    indice = 0

    while tamanho >= 1024 and indice < len(unidades) - 1:

        tamanho /= 1024

        indice += 1

    return f"{tamanho:.2f} {unidades[indice]}"


def info():

    disco_info = disco()

    uploads = tamanho_uploads()

    porcentagem = (
        uploads / disco_info["total"] * 100
        if disco_info["total"] > 0
        else 0
    )

    return {

        "disk": {

            "total": disco_info["total"],
            "used": disco_info["usado"],
            "free": disco_info["livre"],

            "total_formatted": formatar(disco_info["total"]),
            "used_formatted": formatar(disco_info["usado"]),
            "free_formatted": formatar(disco_info["livre"])

        },

        "uploads": {

            "size": uploads,
            "size_formatted": formatar(uploads),
            "percentage": round(porcentagem, 2)

        }

    }