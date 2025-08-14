# app/models.py
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db  # Importa da nossa fábrica


class Residente(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    cpf = db.Column(db.String(20), unique=True, nullable=False)
    crm_uf = db.Column(db.String(2), nullable=False)
    crm_numero = db.Column(db.String(10), nullable=False)
    especialidade_id = db.Column(
        db.Integer, db.ForeignKey("especialidade.id"), nullable=False
    )
    supervisor_id = db.Column(db.Integer, db.ForeignKey("preceptor.id"), nullable=False)
    universidade_id = db.Column(
        db.Integer, db.ForeignKey("universidade.id"), nullable=False
    )
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospital.id"), nullable=False)
    ano_ingresso = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(10), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    senha_hash = db.Column(db.String(256))

    # Relacionamentos
    especialidade = db.relationship("Especialidade", backref="residentes")
    procedimentos = db.relationship(
        "Procedimento", back_populates="residente", lazy="dynamic"
    )
    supervisor = db.relationship(
        "Preceptor", backref="residentes_supervisionados", foreign_keys=[supervisor_id]
    )
    especialidade = db.relationship(
        "Especialidade", backref="residentes", foreign_keys=[especialidade_id]
    )
    universidade = db.relationship(
        "Universidade", backref="residentes", foreign_keys=[universidade_id]
    )
    hospital = db.relationship(
        "Hospital", backref="residentes", foreign_keys=[hospital_id]
    )

    def get_id(self):
        return f"residente-{self.id}"

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha) if self.senha_hash else False


class Preceptor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    cpf = db.Column(db.String(20), unique=True, nullable=False)
    crm_uf = db.Column(db.String(2), nullable=False)
    crm_numero = db.Column(db.String(10), nullable=False)
    universidade_id = db.Column(
        db.Integer, db.ForeignKey("universidade.id"), nullable=False
    )
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospital.id"), nullable=False)
    especialidade_id = db.Column(
        db.Integer, db.ForeignKey("especialidade.id"), nullable=False
    )
    senha_hash = db.Column(db.String(256))
    data_cadastro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    procedimentos_para_validar = db.relationship(
        "Procedimento", back_populates="preceptor", lazy="dynamic"
    )
    universidade = db.relationship(
        "Universidade", backref="preceptores", foreign_keys=[universidade_id]
    )
    hospital = db.relationship(
        "Hospital", backref="preceptores", foreign_keys=[hospital_id]
    )
    especialidade = db.relationship(
        "Especialidade", backref="preceptores", foreign_keys=[especialidade_id]
    )

    def get_id(self):
        return f"preceptor-{self.id}"

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha) if self.senha_hash else False

    def __repr__(self):
        return f"<Preceptor {self.nome}>"


class Procedimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_procedimento = db.Column(db.String(200), nullable=False)
    data_realizacao = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    # Campos metodologia HEIPOC - FAMED UFU
    # H - História clínica resumida (O que vi?)
    historia_clinica = db.Column(db.Text, nullable=False)

    # E - Exame físico (dados mais relevantes)
    exame_fisico = db.Column(db.Text, nullable=False)

    # I - Interpretação/análise/diagnósticos diferenciais
    interpretacao_diagnostico = db.Column(db.Text, nullable=False)

    # P - Plano terapêutico resumido (O que fiz?)
    plano_terapeutico = db.Column(db.Text, nullable=False)

    # O - Orientação ao paciente
    orientacao_paciente = db.Column(db.Text, nullable=False)

    # C - Conhecimento adquirido/necessidade de aprendizagem (O que aprendi?)
    conhecimento_aprendizagem = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), default="Pendente", nullable=False)
    observacao_preceptor = db.Column(db.Text, nullable=True)
    residente_id = db.Column(db.Integer, db.ForeignKey("residente.id"), nullable=False)
    preceptor_id = db.Column(db.Integer, db.ForeignKey("preceptor.id"), nullable=False)
    residente = db.relationship("Residente", back_populates="procedimentos")
    preceptor = db.relationship(
        "Preceptor", back_populates="procedimentos_para_validar"
    )

    def gerar_descricao_completa(self):
        """Gera uma descrição completa seguindo a metodologia HEIPOC da FAMED UFU"""
        descricao_parts = []

        if self.historia_clinica:
            descricao_parts.append(
                f"**H - HISTÓRIA CLÍNICA (O que vi?):**\n{self.historia_clinica}"
            )

        if self.exame_fisico:
            descricao_parts.append(f"**E - EXAME FÍSICO:**\n{self.exame_fisico}")

        if self.interpretacao_diagnostico:
            descricao_parts.append(
                f"**I - INTERPRETAÇÃO/DIAGNÓSTICOS DIFERENCIAIS:**\n{self.interpretacao_diagnostico}"
            )

        if self.plano_terapeutico:
            descricao_parts.append(
                f"**P - PLANO TERAPÊUTICO (O que fiz?):**\n{self.plano_terapeutico}"
            )

        if self.orientacao_paciente:
            descricao_parts.append(
                f"**O - ORIENTAÇÃO AO PACIENTE:**\n{self.orientacao_paciente}"
            )

        if self.conhecimento_aprendizagem:
            descricao_parts.append(
                f"**C - CONHECIMENTO ADQUIRIDO (O que aprendi?):**\n{self.conhecimento_aprendizagem}"
            )

        return "\n\n".join(descricao_parts)


class Universidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), unique=True, nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    hospitais = db.relationship("Hospital", backref="universidade", lazy=True)

    def __repr__(self):
        return f"<Universidade {self.nome}>"


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), unique=True, nullable=False)
    universidade_id = db.Column(
        db.Integer, db.ForeignKey("universidade.id"), nullable=False
    )

    def __repr__(self):
        return f"<Hospital {self.nome}>"


class Especialidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), unique=True, nullable=False)

    def __repr__(self):
        return f"<Especialidade {self.nome}>"
