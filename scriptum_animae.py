# ==========================================================
# 🏛️ SCRIPTUM ANIMAE — ESCRITA DA ALMA
# Versão Profissional Final
# ==========================================================

import tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlite3
import bcrypt
from cryptography.fernet import Fernet
import os
import sys
import speech_recognition as sr
import pyttsx3
import threading
import queue
from PIL import Image, ImageTk

# ==========================================================
# 📁 CAMINHO RECURSOS (FUNCIONA NO .EXE)
# ==========================================================

def caminho_recurso(arquivo):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, arquivo)
    return os.path.join(os.path.abspath("."), arquivo)

# ==========================================================
# 📁 PASTA SEGURA APPDATA
# ==========================================================

APP_DIR = os.path.join(
    os.getenv("LOCALAPPDATA"),
    "ScriptumAnimae"
)

os.makedirs(APP_DIR, exist_ok=True)

# ==========================================================
# 🔐 CRIPTOGRAFIA
# ==========================================================

def carregar_chave():

    caminho = os.path.join(APP_DIR, "secret.key")

    if not os.path.exists(caminho):
        chave = Fernet.generate_key()
        with open(caminho, "wb") as f:
            f.write(chave)
    else:
        with open(caminho, "rb") as f:
            chave = f.read()

    return chave

fernet = Fernet(carregar_chave())

# ==========================================================
# 🗄️ BANCO
# ==========================================================

DB_PATH = os.path.join(APP_DIR, "scriptum_animae.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios(
id INTEGER PRIMARY KEY AUTOINCREMENT,
usuario TEXT UNIQUE,
senha BLOB)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS textos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
usuario TEXT,
texto BLOB,
data TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
""")

conn.commit()
usuario_logado = None

# ==========================================================
# 🔊 VOZ ESTÁVEL
# ==========================================================

engine = pyttsx3.init()
engine.setProperty("rate", 170)

fila_voz = queue.Queue()

def loop_voz():
    while True:
        texto = fila_voz.get()
        if texto is None:
            break
        engine.say(texto)
        engine.runAndWait()

threading.Thread(target=loop_voz, daemon=True).start()

def falar(texto):
    fila_voz.put(texto)

# ==========================================================
# 🎤 OUVIR
# ==========================================================

def ouvir_usuario():

    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:

            falar("Calibrando áudio.")
            recognizer.adjust_for_ambient_noise(source, duration=2)

            falar("Pode falar.")
            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=20
            )

        texto = recognizer.recognize_google(
            audio,
            language="pt-BR"
        )

        falar("Entendi.")
        return texto

    except:
        falar("Não consegui compreender.")
        return ""

# ==========================================================
# 🧠 RESPOSTA TERAPÊUTICA
# ==========================================================

def resposta_terapeutica(frase):

    frase = frase.lower()

    if "triste" in frase:
        return "Sinto muito que esteja se sentindo assim."

    if "ansioso" in frase:
        return "Respire fundo. Vamos com calma."

    if "cansado" in frase:
        return "Parece que você está sobrecarregado."

    if "feliz" in frase:
        return "Fico feliz em ouvir isso."

    return "Estou aqui para ouvir você."

# ==========================================================
# 🤖 ASSISTENTE
# ==========================================================

def assistente_voz():

    def executar():

        frase = ouvir_usuario()
        if not frase:
            return

        resposta = resposta_terapeutica(frase)
        falar(resposta)

        area_texto.insert(
            tk.END,
            f"\n🗣️ Você: {frase}\n💬 Assistente: {resposta}\n"
        )

    threading.Thread(target=executar, daemon=True).start()

# ==========================================================
# 🎤 DITADO
# ==========================================================

def ditado_voz():

    recognizer = sr.Recognizer()

    def executar():

        try:
            with sr.Microphone() as source:

                falar("Calibrando áudio.")
                recognizer.adjust_for_ambient_noise(source, duration=2)

                falar("Pode ditar.")
                audio = recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=30
                )

            texto = recognizer.recognize_google(
                audio,
                language="pt-BR"
            )

            area_texto.insert(tk.END, texto + " ")
            falar("Texto registrado.")

        except:
            falar("Não consegui reconhecer.")

    threading.Thread(target=executar, daemon=True).start()

# ==========================================================
# 🔐 CADASTRO / LOGIN
# ==========================================================

def cadastrar():

    user = entry_user.get()
    senha = entry_pass.get()

    if not user or not senha:
        messagebox.showerror("Erro","Preencha os campos")
        return

    hash_senha = bcrypt.hashpw(
        senha.encode(),
        bcrypt.gensalt()
    )

    try:
        cursor.execute(
            "INSERT INTO usuarios VALUES(NULL,?,?)",
            (user, hash_senha)
        )
        conn.commit()
        messagebox.showinfo("OK","Cadastrado")
    except:
        messagebox.showerror("Erro","Usuário já existe")

def login():

    global usuario_logado

    user = entry_user.get()
    senha = entry_pass.get()

    cursor.execute(
        "SELECT senha FROM usuarios WHERE usuario=?",
        (user,)
    )

    res = cursor.fetchone()

    if res and bcrypt.checkpw(senha.encode(), res[0]):
        usuario_logado = user
        abrir_app()
    else:
        messagebox.showerror("Erro","Login inválido")

# ==========================================================
# 💾 SALVAR / HISTÓRICO
# ==========================================================

def salvar_texto():

    texto = area_texto.get("1.0", tk.END)
    enc = fernet.encrypt(texto.encode())

    cursor.execute(
        "INSERT INTO textos VALUES(NULL,?,?,CURRENT_TIMESTAMP)",
        (usuario_logado, enc)
    )

    conn.commit()
    area_texto.delete("1.0", tk.END)

def carregar_textos():

    lista.delete("1.0", tk.END)

    cursor.execute(
        "SELECT texto,data FROM textos WHERE usuario=?",
        (usuario_logado,)
    )

    for texto,data in cursor.fetchall():

        dec = fernet.decrypt(texto).decode()

        lista.insert(tk.END,f"\n📅 {data}\n{dec}\n")
        lista.insert(tk.END,"-"*50)

# ==========================================================
# 🖥️ APP PRINCIPAL
# ==========================================================

def abrir_app():

    janela_login.destroy()

    app = tk.Tk()
    app.title("Scriptum Animae")
    app.geometry("1000x700")
    app.configure(bg="#E8F1F2")

    # Ícone
    ico = caminho_recurso("logo.ico")
    if os.path.exists(ico):
        app.iconbitmap(ico)

    # Logo
    try:
        img = Image.open(caminho_recurso("logo.png"))
        img = img.resize((140,140))
        logo_app = ImageTk.PhotoImage(img)

        lbl_logo = tk.Label(app,image=logo_app,bg="#E8F1F2")
        lbl_logo.image = logo_app
        lbl_logo.pack(pady=5)

    except Exception as e:
        print(e)

    global area_texto, lista

    area_texto = scrolledtext.ScrolledText(app,width=110,height=10)
    area_texto.pack()

    tk.Button(app,text="🎤 Ditado",command=ditado_voz).pack(pady=2)
    tk.Button(app,text="🤖 Assistente",command=assistente_voz).pack(pady=2)
    tk.Button(app,text="💾 Salvar",command=salvar_texto).pack(pady=2)
    tk.Button(app,text="📜 Histórico",command=carregar_textos).pack(pady=2)

    lista = scrolledtext.ScrolledText(app,width=110,height=20)
    lista.pack()

    app.mainloop()

# ==========================================================
# LOGIN UI
# ==========================================================

janela_login = tk.Tk()
janela_login.title("Scriptum Animae — Login")
janela_login.configure(bg="#E8F1F2")

ico = caminho_recurso("logo.ico")
if os.path.exists(ico):
    janela_login.iconbitmap(ico)

try:
    img = Image.open(caminho_recurso("logo.png"))
    img = img.resize((180,180))
    logo_login = ImageTk.PhotoImage(img)

    lbl_logo = tk.Label(janela_login,image=logo_login,bg="#E8F1F2")
    lbl_logo.image = logo_login
    lbl_logo.pack(pady=5)

except Exception as e:
    print(e)

entry_user = tk.Entry(janela_login)
entry_user.pack(pady=2)

entry_pass = tk.Entry(janela_login,show="*")
entry_pass.pack(pady=2)

tk.Button(janela_login,text="Cadastrar",command=cadastrar).pack(pady=2)
tk.Button(janela_login,text="Login",command=login).pack(pady=2)

janela_login.mainloop()
