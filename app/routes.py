# app/routes.py
import requests
from flask import (
    Blueprint,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.email import send_procedimento_avaliado_email
from app.forms import (
    AvaliacaoForm,
    LoginForm,
    ProcedimentoForm,
    RegistroForm,
    RegistroPreceptorForm,
    VerificacaoCRMForm,
)
from app.models import (
    Hospital,
    Preceptor,
    Procedimento,
    Residente,
    Universidade,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return redirect(url_for("main.login"))


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = (
            Residente.query.filter_by(email=email).first()
            or Preceptor.query.filter_by(email=email).first()
        )
        if user and user.check_senha(password):
            login_user(user)
            return redirect(url_for("main.home"))
        else:
            flash("Invalid login. Please check your email and password.", "danger")
    return render_template("login.html", title="Login", form=form)


@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("main.login"))


@main_bp.route("/home")
@login_required
def home():
    if isinstance(current_user, Residente):
        return redirect(url_for("main.dashboard_residente"))
    elif isinstance(current_user, Preceptor):
        return redirect(url_for("main.dashboard_preceptor"))
    return redirect(url_for("main.login"))


@main_bp.route("/dashboard/residente", methods=["GET", "POST"])
@login_required
def dashboard_residente():
    if not isinstance(current_user, Residente):
        flash("Unauthorized access.", "danger")
        return redirect(url_for("main.home"))
    form = ProcedimentoForm()
    if form.validate_on_submit():
        novo_procedimento = Procedimento(
            nome_procedimento=form.nome_procedimento.data,
            data_realizacao=form.data_realizacao.data,
            historia_clinica=form.historia_clinica.data,
            exame_fisico=form.exame_fisico.data,
            interpretacao_diagnostico=form.interpretacao_diagnostico.data,
            plano_terapeutico=form.plano_terapeutico.data,
            orientacao_paciente=form.orientacao_paciente.data,
            conhecimento_aprendizagem=form.conhecimento_aprendizagem.data,
            residente_id=current_user.id,
            preceptor_id=form.preceptor.data.id,
        )

        db.session.add(novo_procedimento)
        db.session.commit()
        flash("Procedure registered successfully! Awaiting validation.", "success")
        return redirect(url_for("main.dashboard_residente"))

        db.session.add(novo_procedimento)
        db.session.commit()
        flash("Procedure registered successfully! Awaiting validation.", "success")
        return redirect(url_for("main.dashboard_residente"))
    procedimentos = (
        Procedimento.query.filter_by(residente_id=current_user.id)
        .order_by(Procedimento.data_realizacao.desc())
        .all()
    )
    return render_template(
        "dashboard_residente.html",
        title="My Dashboard",
        form=form,
        procedimentos=procedimentos,
    )


@main_bp.route("/dashboard/preceptor", methods=["GET", "POST"])
@login_required
def dashboard_preceptor():
    if not isinstance(current_user, Preceptor):
        flash("Unauthorized access.", "danger")
        return redirect(url_for("main.home"))
    form = AvaliacaoForm()
    if form.validate_on_submit():
        procedimento_id = form.procedimento_id.data
        procedimento = db.session.get(Procedimento, procedimento_id)
        if not procedimento:
            flash("Procedure not found.", "danger")
        elif procedimento.preceptor_id != current_user.id:
            flash("You do not have permission to evaluate this procedure.", "danger")
        else:
            procedimento.observacao_preceptor = form.observacao.data
            if form.validar.data:
                procedimento.status = "Validado"
                send_procedimento_avaliado_email(
                    procedimento.residente, procedimento, "Validado"
                )
                flash(
                    f'Procedure "{procedimento.nome_procedimento}" successfully validated! Email sent to the resident.',
                    "success",
                )
            elif form.rejeitar.data:
                procedimento.status = "Rejeitado"
                send_procedimento_avaliado_email(
                    procedimento.residente, procedimento, "Rejeitado"
                )
                flash(
                    f'Procedure "{procedimento.nome_procedimento}" rejected. Email sent to the resident.',
                    "warning",
                )
            db.session.commit()
        return redirect(url_for("main.dashboard_preceptor"))
    procedimentos_pendentes = (
        Procedimento.query.filter_by(preceptor_id=current_user.id, status="Pendente")
        .order_by(Procedimento.data_realizacao.asc())
        .all()
    )
    procedimentos_avaliados = (
        Procedimento.query.filter(
            Procedimento.preceptor_id == current_user.id,
            Procedimento.status != "Pendente",
        )
        .order_by(Procedimento.data_realizacao.desc())
        .all()
    )
    residentes_supervisionados = (
        db.session.query(Residente)
        .join(Procedimento)
        .filter(Procedimento.preceptor_id == current_user.id)
        .distinct()
        .all()
    )
    return render_template(
        "dashboard_preceptor.html",
        title="Preceptor Dashboard",
        pendentes=procedimentos_pendentes,
        avaliados=procedimentos_avaliados,
        residentes=residentes_supervisionados,
        form_avaliacao=form,
    )


@main_bp.route("/relatorio/residente/<int:residente_id>")
@login_required
def gerar_relatorio(residente_id):
    residente = db.session.get(Residente, residente_id)

    if not residente:
        flash("Resident not found.", "danger")
        return redirect(url_for("main.home"))

    if isinstance(current_user, Residente):
        if current_user.id != residente_id:
            flash("Access denied. You can only access your own report.", "danger")
            return redirect(url_for("main.dashboard_residente"))
    elif isinstance(current_user, Preceptor):
        if residente.supervisor_id != current_user.id:
            flash(
                "Access denied. You can only access reports of residents under your supervision.",
                "danger",
            )
            return redirect(url_for("main.dashboard_preceptor"))
    else:
        flash("Access denied.", "danger")
        return redirect(url_for("main.home"))

    procedimentos_validados = (
        Procedimento.query.filter_by(residente_id=residente.id, status="Validado")
        .order_by(Procedimento.data_realizacao.asc())
        .all()
    )

    from collections import Counter
    from datetime import datetime

    import pytz

    brasil_tz = pytz.timezone("America/Sao_Paulo")
    data_emissao_local = datetime.now(brasil_tz)

    total_procedimentos = len(procedimentos_validados)
    procedimentos_pendentes = Procedimento.query.filter_by(
        residente_id=residente.id, status="Pendente"
    ).count()
    procedimentos_rejeitados = Procedimento.query.filter_by(
        residente_id=residente.id, status="Rejeitado"
    ).count()
    total_geral = (
        total_procedimentos + procedimentos_pendentes + procedimentos_rejeitados
    )

    preceptores_stats = Counter(
        [proc.preceptor.nome for proc in procedimentos_validados]
    )

    try:
        from weasyprint import CSS, HTML
        from weasyprint.text.fonts import FontConfiguration

        html_renderizado = render_template(
            "relatorio_template.html",
            residente=residente,
            procedimentos=procedimentos_validados,
            data_emissao=data_emissao_local,
            total_procedimentos=total_procedimentos,
            procedimentos_pendentes=procedimentos_pendentes,
            procedimentos_rejeitados=procedimentos_rejeitados,
            total_geral=total_geral,
            preceptores_stats=preceptores_stats,
        )

        font_config = FontConfiguration()

        css_string = """
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "Hospital de Clínicas - UFU";
                font-size: 10px;
                color: #666;
            }
            @bottom-right {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10px;
                color: #666;
            }
        }
        body {
            font-family: 'DejaVu Sans', Arial, sans-serif;
            line-height: 1.4;
            color: #333;
        }
        .header-institucional {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #003366;
            padding-bottom: 15px;
        }
        .header-institucional h1 {
            color: #003366;
            font-size: 16px;
            margin: 5px 0;
        }
        .header-institucional h2 {
            color: #0066CC;
            font-size: 14px;
            margin: 5px 0;
        }
        .titulo-principal {
            text-align: center;
            color: #003366;
            font-size: 18px;
            font-weight: bold;
            margin: 20px 0;
        }
        .secao {
            margin-bottom: 25px;
        }
        .secao h3 {
            color: #0066CC;
            font-size: 14px;
            font-weight: bold;
            border-bottom: 1px solid #0066CC;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }
        .dados-residente {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .dados-residente td {
            padding: 8px;
            border: 1px solid #ddd;
        }
        .dados-residente td:first-child {
            font-weight: bold;
            background-color: #f0f4f8;
            width: 30%;
        }
        .estatisticas {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .estatisticas th {
            background-color: #003366;
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: bold;
        }
        .estatisticas td {
            padding: 8px;
            text-align: center;
            border: 1px solid #ddd;
        }
        .estatisticas tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .procedimentos {
            width: 100%;
            border-collapse: collapse;
            font-size: 9px;
        }
        .procedimentos th {
            background-color: #003366;
            color: white;
            padding: 8px;
            text-align: center;
            font-weight: bold;
        }
        .procedimentos td {
            padding: 6px;
            border: 1px solid #ddd;
            text-align: center;
        }
        .procedimentos tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .observacoes {
            text-align: justify;
            line-height: 1.6;
            margin: 20px 0;
        }
        .rodape {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ccc;
            font-size: 8px;
            color: #666;
        }
        """

        html_doc = HTML(string=html_renderizado)
        css_doc = CSS(string=css_string, font_config=font_config)
        pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc], font_config=font_config)

        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = (
            f'attachment; filename=report_{residente.nome.replace(" ", "_").lower()}.pdf'
        )
        return response

    except ImportError as e:
        print(f"WeasyPrint not available: {e}")
        flash("Warning: WeasyPrint is not installed. Viewing as HTML.", "info")
        html_renderizado = render_template(
            "relatorio_template.html",
            residente=residente,
            procedimentos=procedimentos_validados,
            data_emissao=data_emissao_local,
            total_procedimentos=total_procedimentos,
            procedimentos_pendentes=procedimentos_pendentes,
            procedimentos_rejeitados=procedimentos_rejeitados,
            total_geral=total_geral,
            preceptores_stats=preceptores_stats,
        )
        response = make_response(html_renderizado)
        response.headers["Content-Type"] = "text/html"
        return response
    except Exception as e:
        print(f"Error generating PDF: {e}")
        flash("Error generating PDF. Viewing as HTML.", "warning")
        html_renderizado = render_template(
            "relatorio_template.html",
            residente=residente,
            procedimentos=procedimentos_validados,
            data_emissao=data_emissao_local,
            total_procedimentos=total_procedimentos,
            procedimentos_pendentes=procedimentos_pendentes,
            procedimentos_rejeitados=procedimentos_rejeitados,
            total_geral=total_geral,
            preceptores_stats=preceptores_stats,
        )
        response = make_response(html_renderizado)
        response.headers["Content-Type"] = "text/html"
        return response


@main_bp.route("/verificar-crm", methods=["GET", "POST"])
def verificar_crm():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = VerificacaoCRMForm()
    if form.validate_on_submit():
        uf = form.uf.data
        crm = form.crm.data

        url = "https://portal.cfm.org.br/api_rest_php/api/v1/medicos/buscar_medicos"
        headers = {"Content-Type": "application/json"}
        payload = {
            "medico": {
                "crmMedico": crm,
                "ufMedico": uf,
            },
            "page": 1,
            "pageNumber": 1,
            "pageSize": 10,
        }

        try:
            response = requests.post(url, json=[payload], headers=headers, timeout=10)
            response.raise_for_status()
            resultado = response.json()
        except requests.exceptions.RequestException as e:
            flash(f"Error accessing external API: {str(e)}", "danger")
            return render_template(
                "verificar_crm.html", title="Step 1: CRM Verification", form=form
            )

        if resultado and resultado.get("dados"):
            dados_medico = resultado["dados"][0]
            quantidade_encontrada = int(dados_medico.get("COUNT", 0))

            if quantidade_encontrada == 1:
                situacao = dados_medico.get("SITUACAO")
                if situacao == "Regular":
                    session["crm_verificado"] = {
                        "uf": uf,
                        "crm": crm,
                    }
                    flash(
                        "CRM is regular! Please complete your registration.",
                        "success",
                    )
                    return redirect(url_for("main.selecionar_perfil"))
                else:
                    flash(
                        f"CRM found, but its status is '{situacao}'. Only regular CRMs can register.",
                        "danger",
                    )
            else:
                flash("CRM not found or invalid. Please try again.", "danger")
        else:
            flash("CRM not found or invalid. Please try again.", "danger")

    return render_template(
        "verificar_crm.html", title="Step 1: CRM Verification", form=form
    )


@main_bp.route("/selecionar-perfil")
def selecionar_perfil():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if "crm_verificado" not in session:
        flash("Please verify your CRM first.", "info")
        return redirect(url_for("main.verificar_crm"))

    return render_template("selecionar_perfil.html", title="Step 2: Profile Selection")


@main_bp.route("/registrar", methods=["GET", "POST"])
def registrar():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    if "crm_verificado" not in session:
        flash("Please verify your CRM first.", "info")
        return redirect(url_for("main.verificar_crm"))

    form = RegistroForm()
    if request.method == "GET":
        form.nome.data = session["crm_verificado"].get("nome", "")

    if form.validate_on_submit():
        if Residente.query.filter_by(email=form.email.data).first():
            flash("This email is already in use.", "danger")
        elif Residente.query.filter_by(cpf=form.cpf.data).first():
            flash("This CPF is already registered.", "danger")
        else:
            crm_info = session.get("crm_verificado", {})

            universidade = Universidade.query.filter_by(
                nome=form.instituicao.data
            ).first()
            hospital = Hospital.query.filter_by(
                nome="Hospital de Clínicas de Uberlândia (HC-UFU)"
            ).first()

            if not universidade:
                universidade = Universidade.query.first()
                if not universidade:
                    flash("Error: No university found in the system.", "danger")
                    return render_template(
                        "registrar.html",
                        title="Complete Registration: Resident",
                        form=form,
                    )

            if not hospital:
                hospital = Hospital.query.first()
                if not hospital:
                    flash("Error: No hospital found in the system.", "danger")
                    return render_template(
                        "registrar.html",
                        title="Complete Registration: Resident",
                        form=form,
                    )

            novo_residente = Residente(
                nome=form.nome.data,
                email=form.email.data,
                celular=form.celular.data,
                cpf=form.cpf.data,
                crm_uf=crm_info.get("uf"),
                crm_numero=crm_info.get("crm"),
                especialidade_id=form.especialidade.data.id,
                supervisor_id=form.supervisor.data.id,
                universidade_id=universidade.id,
                hospital_id=hospital.id,
                ano_ingresso=int(form.ano_ingresso.data),
                categoria=form.categoria.data,
            )
            novo_residente.set_senha(form.password.data)
            db.session.add(novo_residente)
            db.session.commit()
            session.pop("crm_verificado", None)
            flash(
                "Registration completed successfully! You can now log in.",
                "success",
            )
            return redirect(url_for("main.login"))
    return render_template(
        "registrar.html", title="Complete Registration: Resident", form=form
    )


@main_bp.route("/registrar-preceptor", methods=["GET", "POST"])
def registrar_preceptor():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if "crm_verificado" not in session:
        flash("Please verify your CRM first.", "info")
        return redirect(url_for("main.verificar_crm"))

    form = RegistroPreceptorForm()
    if request.method == "GET":
        form.nome.data = session["crm_verificado"].get("nome", "")

    if form.validate_on_submit():
        if Preceptor.query.filter_by(email=form.email.data).first():
            flash("This email is already in use. Please choose another.", "danger")
        elif Preceptor.query.filter_by(cpf=form.cpf.data).first():
            flash("This CPF is already registered.", "danger")
        else:
            universidade = Universidade.query.filter_by(
                nome=form.instituicao.data
            ).first()
            hospital = Hospital.query.filter_by(nome=form.hospital.data).first()

            if not universidade or not hospital:
                flash(
                    "Configuration error: The default institution or hospital was not found in the database.",
                    "danger",
                )
                return render_template(
                    "registrar_preceptor.html",
                    title="Complete Registration: Preceptor",
                    form=form,
                )
            crm_info = session.get("crm_verificado", {})

            novo_preceptor = Preceptor(
                nome=form.nome.data,
                email=form.email.data,
                celular=form.celular.data,
                cpf=form.cpf.data,
                crm_uf=crm_info.get("uf"),
                crm_numero=crm_info.get("crm"),
                universidade_id=universidade.id,
                hospital_id=hospital.id,
                especialidade_id=form.supervisor.data.id,
            )
            novo_preceptor.set_senha(form.password.data)
            db.session.add(novo_preceptor)
            db.session.commit()

            session.pop("crm_verificado", None)
            flash(
                "Preceptor registration completed successfully! You can now log in.",
                "success",
            )
            return redirect(url_for("main.login"))

    return render_template(
        "registrar_preceptor.html", title="Complete Registration: Preceptor", form=form
    )
