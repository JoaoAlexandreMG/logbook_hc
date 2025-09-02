# app/forms.py
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    HiddenField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
    Optional,
)
from wtforms_sqlalchemy.fields import QuerySelectField

# Importe seus modelos para usar nas queries dos formulários
from app.models import Especialidade, Hospital, Preceptor, Universidade


# Garante que só retorna preceptores distintos e válidos
def preceptor_query():
    return Preceptor.query


# Crie duas novas funções de query para os campos de seleção
def universidade_query():
    return Universidade.query


def hospital_query():
    return Hospital.query


def especialidade_query():
    return Especialidade.query.order_by(Especialidade.nome)


class RegistroForm(FlaskForm):
    nome = StringField("Nome Completo", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    celular = StringField("Número de Celular", validators=[DataRequired()])
    cpf = StringField("CPF", validators=[DataRequired()])
    instituicao = StringField(
        "Instituição de Ensino",
        default="Universidade Federal de Uberlândia",
        render_kw={"readonly": True},
    )
    hospital = StringField("Hospital", default="HC-UFU", render_kw={"readonly": True})
    # ADICIONE este novo campo no lugar:

    especialidade = QuerySelectField(
        "Especialidade da Residência",
        query_factory=especialidade_query,
        get_label="nome",
        allow_blank=True,
        blank_text="-- Selecione sua especialidade --",
        validators=[DataRequired()],
    )
    supervisor = QuerySelectField(
        "Selecione seu Supervisor",
        query_factory=preceptor_query,
        get_label="nome",
        allow_blank=True,
        blank_text="-- Selecione um supervisor --",
        validators=[DataRequired()],
    )
    ano_ingresso = StringField("Ano de Ingresso", validators=[DataRequired()])
    categoria = SelectField(
        "Categoria",
        choices=[("R1", "R1"), ("R2", "R2"), ("R3", "R3"), ("R4", "R4"), ("R+", "R+")],
        validators=[DataRequired()],
    )
    password = PasswordField(
        "Criar uma Senha", validators=[DataRequired(), Length(min=8)]
    )
    confirm_password = PasswordField(
        "Confirmar Senha",
        validators=[
            DataRequired(),
            EqualTo("password", message="As senhas devem coincidir."),
        ],
    )
    submit = SubmitField("Finalizar Cadastro")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Entrar")


class ProcedimentoForm(FlaskForm):
    nome_procedimento = StringField(
        "Nome do Procedimento", validators=[DataRequired(), Length(min=5, max=200)]
    )
    data_realizacao = DateField(
        "Data de Realização", format="%Y-%m-%d", validators=[InputRequired()]
    )
    preceptor = QuerySelectField(
        "Preceptor Responsável",
        query_factory=preceptor_query,
        get_label="nome",
        allow_blank=False,
        validators=[DataRequired()],
    )

    # Metodologia HEIPOC - FAMED UFU
    historia_clinica = TextAreaField(
        "H - História Clínica (O que vi?)",
        validators=[DataRequired(), Length(min=20, max=2000)],
        render_kw={
            "placeholder": "História clínica resumida. Incluir dados de identificação (idade e gênero). Descreva o que você observou no paciente, queixa principal, história da doença atual..."
        },
    )

    exame_fisico = TextAreaField(
        "E - Exame Físico",
        validators=[DataRequired(), Length(min=15, max=2000)],
        render_kw={
            "placeholder": "Dados mais relevantes do exame físico. Descreva os achados significativos encontrados durante a avaliação clínica..."
        },
    )

    interpretacao_diagnostico = TextAreaField(
        "I - Interpretação/Diagnósticos Diferenciais",
        validators=[DataRequired(), Length(min=15, max=2000)],
        render_kw={
            "placeholder": "Sua interpretação dos achados, análise do caso e principais diagnósticos diferenciais considerados..."
        },
    )

    plano_terapeutico = TextAreaField(
        "P - Plano Terapêutico (O que fiz?)",
        validators=[DataRequired(), Length(min=15, max=2000)],
        render_kw={
            "placeholder": "Plano terapêutico resumido. Descreva as condutas, procedimentos e tratamentos realizados..."
        },
    )

    orientacao_paciente = TextAreaField(
        "O - Orientação ao Paciente",
        validators=[DataRequired(), Length(min=10, max=1500)],
        render_kw={
            "placeholder": "Orientações fornecidas ao paciente sobre o quadro, tratamento, cuidados e seguimento..."
        },
    )

    conhecimento_aprendizagem = TextAreaField(
        "C - Conhecimento Adquirido (O que aprendi?)",
        validators=[DataRequired(), Length(min=15, max=2000)],
        render_kw={
            "placeholder": "Conhecimento adquirido ou necessidade de aprendizagem estabelecida. Incluir fontes de busca sugeridas..."
        },
    )

    submit = SubmitField("Registrar Procedimento")


class AvaliacaoForm(FlaskForm):
    procedimento_id = HiddenField(validators=[DataRequired()])
    observacao = TextAreaField(
        "Observações / Justificativa", validators=[Optional(), Length(max=5000)]
    )
    validar = SubmitField("Validar Procedimento")
    rejeitar = SubmitField("Rejeitar Procedimento")


class RegistroPreceptorForm(FlaskForm):
    nome = StringField("Nome Completo", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    celular = StringField("Número de Celular", validators=[DataRequired()])
    cpf = StringField("CPF", validators=[DataRequired()])

    # --- ALTERAÇÃO AQUI ---
    # Troca dos campos de texto por campos de seleção
    instituicao = StringField(
        "Instituição de Ensino Superior",
        default="Universidade Federal de Uberlândia",
        render_kw={"readonly": True},
    )
    hospital = StringField(
        "Hospital Principal",
        default="Hospital de Clínicas de Uberlândia (HC-UFU)",
        render_kw={"readonly": True},
    )
    # O campo UF foi removido do formulário, pois agora está atrelado à universidade.

    supervisor = QuerySelectField(
        "Especialidade Principal",
        query_factory=especialidade_query,
        get_label="nome",
        allow_blank=True,
        blank_text="-- Selecione sua especialidade --",
        validators=[DataRequired()],
    )

    password = PasswordField(
        "Criar uma Senha", validators=[DataRequired(), Length(min=8)]
    )
    confirm_password = PasswordField(
        "Confirmar Senha",
        validators=[
            DataRequired(),
            EqualTo("password", message="As senhas devem coincidir."),
        ],
    )
    submit = SubmitField("Finalizar Cadastro")


class VerificacaoCRMForm(FlaskForm):
    ufs = [
        ("AC", "AC"),
        ("AL", "AL"),
        ("AP", "AP"),
        ("AM", "AM"),
        ("BA", "BA"),
        ("CE", "CE"),
        ("DF", "DF"),
        ("ES", "ES"),
        ("GO", "GO"),
        ("MA", "MA"),
        ("MT", "MT"),
        ("MS", "MS"),
        ("MG", "MG"),
        ("PA", "PA"),
        ("PB", "PB"),
        ("PR", "PR"),
        ("PE", "PE"),
        ("PI", "PI"),
        ("RJ", "RJ"),
        ("RN", "RN"),
        ("RS", "RS"),
        ("RO", "RO"),
        ("RR", "RR"),
        ("SC", "SC"),
        ("SP", "SP"),
        ("SE", "SE"),
        ("TO", "TO"),
    ]
    uf = SelectField("Estado (UF)", choices=ufs, validators=[DataRequired()])
    crm = StringField(
        "Número do CRM", validators=[DataRequired(), Length(min=1, max=10)]
    )
    submit = SubmitField("Verificar CRM")
