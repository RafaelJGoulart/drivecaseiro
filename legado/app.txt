from builtins import print
import io
import time
import socket
import base64
import ctypes
import threading

from flask import request
from flask import redirect

import os

import qrcode
import webview

from flask import Flask
from flask import render_template

# ==================================================
# CORREÇÃO DPI WINDOWS
# ==================================================

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# ==================================================
# CONFIGURAÇÃO
# ==================================================

PORTA = 5000

LARGURA_JANELA = 340
ALTURA_JANELA = 460

MARGEM = 10

# ==================================================
# FLASK
# ==================================================

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

@app.route(
    "/upload",
    methods=["POST"]
)
def upload():

    if "arquivo" not in request.files:
        return redirect("/")

    arquivo = request.files["arquivo"]

    if arquivo.filename == "":
        return redirect("/")

    caminho = os.path.join(
        UPLOAD_FOLDER,
        arquivo.filename
    )

    arquivo.save(caminho)

    return redirect("/?sucesso=1")


# ==================================================
# OBTER IP LOCAL
# ==================================================

def obter_ip():

    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    try:

        s.connect(("8.8.8.8", 80))

        ip = s.getsockname()[0]

    except Exception:

        ip = "127.0.0.1"

    finally:

        s.close()

    return ip


# ==================================================
# GERAR QR CODE EM MEMÓRIA
# ==================================================

def gerar_qr_base64(url):

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(url)

    qr.make(fit=True)

    img = qr.make_image()

    buffer = io.BytesIO()

    img.save(
        buffer,
        format="PNG"
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


# ==================================================
# INICIAR FLASK
# ==================================================

def iniciar_flask():

    app.run(
        host="0.0.0.0",
        port=PORTA,
        debug=False,
        use_reloader=False
    )


# ==================================================
# POSICIONAR JANELA
# ==================================================

def posicionar_janela():

    time.sleep(2)

    hwnd = ctypes.windll.user32.FindWindowW(
        None,
        "MeuDrive"
    )

    if not hwnd:
        print("Janela não encontrada")
        return

    class RECT(ctypes.Structure):

        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long)
        ]

    # Obtém o tamanho real da janela
    rect = RECT()

    ctypes.windll.user32.GetWindowRect(
        hwnd,
        ctypes.byref(rect)
    )

    largura_real = rect.right - rect.left
    altura_real = rect.bottom - rect.top

    # Obtém a área útil da tela
    # (já descontando a barra de tarefas)
    work_area = RECT()

    ctypes.windll.user32.SystemParametersInfoW(
        0x0030,  # SPI_GETWORKAREA
        0,
        ctypes.byref(work_area),
        0
    )

    largura_util = work_area.right
    altura_util = work_area.bottom

    x = largura_util - largura_real - MARGEM
    y = altura_util - altura_real - MARGEM

    ctypes.windll.user32.MoveWindow(
        hwnd,
        x,
        y,
        largura_real,
        altura_real,
        True
    )

    HWND_BOTTOM = 1

    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOACTIVATE = 0x0010

    ctypes.windll.user32.SetWindowPos(
        hwnd,
        HWND_BOTTOM,
        0,
        0,
        0,
        0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
    )

    print(
        f"Janela posicionada em ({x}, {y})"
    )

# ==================================================
# HTML DA JANELA
# ==================================================

def criar_html(qr_base64, url):

    return f"""
<!DOCTYPE html>

<html lang="pt-BR">

<head>

<meta charset="UTF-8">

<style>

* {{
    margin:0;
    padding:0;
    box-sizing:border-box;
}}

body {{

    background:#111;

    color:white;

    min-height:100vh;

    display:flex;

    justify-content:center;

    align-items:center;

    font-family:
        -apple-system,
        BlinkMacSystemFont,
        Arial,
        sans-serif;
}}

.container {{

    text-align:center;

    padding:20px;
}}

h2 {{

    margin-bottom:20px;
}}

.qr {{

    width:250px;

    background:white;

    padding:10px;

    border-radius:12px;

    box-shadow:
        0 0 20px rgba(0,0,0,.4);
}}

.url {{

    margin-top:15px;

    color:#aaa;

    font-size:13px;

    word-break:break-all;
}}

.status {{

    margin-top:12px;
    color:#4CAF50;
    font-size:13px;
    background-color:rgba(76, 175, 80, 0.125);
    border-radius:8px;
    padding: 4px 0px;
}}

</style>

</head>

<body>

<div class="container">

    <h2>Escaneie para conectar</h2>

    <img
        class="qr"
        src="data:image/png;base64,{qr_base64}"
    >

    <div class="url">
        {url}
    </div>

    <div class="status">
        Servidor iniciado com sucesso
    </div>

</div>

</body>

</html>
"""


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    ip = obter_ip()

    url = f"http://{ip}:{PORTA}"

    print()
    print("=" * 50)
    print("MeuDrive iniciado")
    print(f"URL: {url}")
    print("=" * 50)
    print()

    qr_base64 = gerar_qr_base64(url)

    html = criar_html(
        qr_base64,
        url
    )

    flask_thread = threading.Thread(
        target=iniciar_flask,
        daemon=True
    )

    flask_thread.start()

    janela = webview.create_window(
        title="MeuDrive",
        html=html,
        width=LARGURA_JANELA,
        height=ALTURA_JANELA,
        resizable=False,
        on_top=False
    )

    threading.Thread(
        target=posicionar_janela,
        daemon=True
    ).start()

    webview.start()