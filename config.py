# config.py
import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# Carrega as variáveis do arquivo .env
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "uma-chave-secreta-muito-dificil-de-adivinhar"
    )

    # IMPORTANTE: Força o uso do residentes.db na pasta RAIZ, nunca na pasta instance
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "residentes.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações de Email
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "smtp.gmail.com"
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = (
        os.environ.get("MAIL_DEFAULT_SENDER") or "noreply@logbook-residente.com"
    )
