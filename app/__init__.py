# app/__init__.py (versão completa e correta)

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from config import Config

# 1. Cria as instâncias das extensões, mas sem inicializá-las
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "main.login"  # Aponta para o login dentro do Blueprint
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    """Carrega o usuário da sessão a partir do ID."""
    # Importamos os modelos aqui dentro para evitar importações circulares
    from app.models import Preceptor, Residente

    user_type, user_db_id = user_id.split("-")
    if user_type == "residente":
        return db.session.get(Residente, int(user_db_id))
    elif user_type == "preceptor":
        return db.session.get(Preceptor, int(user_db_id))
    return None


def create_app(config_class=Config):
    """Cria e configura a instância da aplicação Flask."""
    # Cria a aplicação Flask SEM usar a pasta instance
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class)

    # 2. Inicializa as extensões com a aplicação criada
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # 3. Importa e registra os Blueprints (onde estão as rotas)
    from app.routes import main_bp

    app.register_blueprint(main_bp)

    # 4. Verifica e cria apenas tabelas que não existem
    with app.app_context():
        # Importa os modelos para garantir que sejam registrados
        # Verifica se as tabelas existem antes de criar
        from sqlalchemy import inspect

        # from app.models import (
        #     Especialidade,
        #     Hospital,
        #     Preceptor,
        #     Procedimento,
        #     Residente,
        #     Universidade,
        # )

        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        # Lista das tabelas esperadas
        expected_tables = [
            "residente",
            "preceptor",
            "procedimento",
            "universidade",
            "hospital",
            "especialidade",
        ]

        # Verifica se alguma tabela importante está faltando
        missing_tables = [
            table for table in expected_tables if table not in existing_tables
        ]

        if missing_tables:
            db.create_all()

    return app
