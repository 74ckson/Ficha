"""
Gerador de Ficha Catalográfica – Streamlit
Padrão: AACR2 + Biblioteca Universitária – UFC
PDF nativo via reportlab + CSS customizado
"""

import unicodedata
import tempfile
import os
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


# ═════════════════════════════════════════════════════════════
# CSS Customizado
# ═════════════════════════════════════════════════════════════

def injetar_css():
    st.markdown(
        """
        <style>
        /* ── Reset e fundo ───────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        :root {
            --primary: #1e3a5f;
            --primary-light: #2d5a8e;
            --accent: #c8a951;
            --accent-hover: #d4b85e;
            --bg-card: #ffffff;
            --bg-app: #f0f2f6;
            --text: #1a1a2e;
            --text-muted: #6b7280;
            --border: #e0e0e0;
            --radius: 12px;
            --shadow: 0 2px 12px rgba(0,0,0,0.06);
            --shadow-hover: 0 4px 20px rgba(0,0,0,0.10);
        }

        /* Fundo */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f0 100%);
        }

        /* Fonte global */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* ── Header ─────────────────────────────────────── */
        .main-header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: white;
            padding: 28px 36px;
            border-radius: var(--radius);
            margin-bottom: 24px;
            box-shadow: var(--shadow);
        }
        .main-header h1 {
            color: white !important;
            font-size: 1.75rem !important;
            font-weight: 700 !important;
            margin: 0 0 4px 0 !important;
            letter-spacing: -0.5px;
        }
        .main-header p {
            color: rgba(255,255,255,0.8) !important;
            font-size: 0.9rem !important;
            margin: 0 !important;
            font-weight: 300;
        }

        /* ── Cards de seção ────────────────────────────── */
        .section-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 20px 24px 16px 24px;
            margin-bottom: 16px;
            box-shadow: var(--shadow);
            transition: box-shadow 0.2s ease;
        }
        .section-card:hover {
            box-shadow: var(--shadow-hover);
        }

        .section-title {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--primary);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 14px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--accent);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* ── Labels e inputs ───────────────────────────── */
        label[data-baseweb="select"] p,
        label[data-baseweb="base-input"] p,
        .stTextInput label,
        .stSelectbox label {
            font-size: 0.78rem !important;
            font-weight: 500 !important;
            color: var(--text-muted) !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stNumberInput > div > div > input {
            border: 1.5px solid var(--border) !important;
            border-radius: 8px !important;
            font-size: 0.88rem !important;
            padding: 8px 12px !important;
            transition: border-color 0.2s, box-shadow 0.2s !important;
        }

        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: var(--primary-light) !important;
            box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.1) !important;
        }

        /* ── Preview box ───────────────────────────────── */
        .preview-container {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 24px;
            box-shadow: var(--shadow);
            margin-bottom: 16px;
        }

        .preview-container .stTextArea {
            background: transparent;
        }

        .preview-container textarea {
            font-family: 'JetBrains Mono', 'Courier New', monospace !important;
            font-size: 0.75rem !important;
            line-height: 1.65 !important;
            background: #fafbfc !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            color: var(--text) !important;
        }

        /* ── Botão PDF ─────────────────────────────────── */
        .btn-pdf {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 28px !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            cursor: pointer;
            transition: transform 0.15s, box-shadow 0.2s !important;
            box-shadow: 0 2px 8px rgba(30, 58, 95, 0.25) !important;
        }
        .btn-pdf:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 16px rgba(30, 58, 95, 0.35) !important;
        }

        /* ── Footer ────────────────────────────────────── */
        .footer {
            text-align: center;
            padding: 20px;
            color: var(--text-muted);
            font-size: 0.78rem;
        }

        /* ── Responsivo ────────────────────────────────── */
        @media (max-width: 768px) {
            .main-header { padding: 20px; }
            .main-header h1 { font-size: 1.3rem !important; }
            .section-card { padding: 16px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ═════════════════════════════════════════════════════════════
# Utilitários
# ═════════════════════════════════════════════════════════════

def remover_acentos(texto: str) -> str:
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.category(c).startswith("M"))


def extrair_vogais(texto: str, limite: int = 3) -> str:
    texto_limpo = remover_acentos(texto).lower()
    resultado = ""
    for c in texto_limpo:
        if c in "aeiou":
            resultado += c
            if len(resultado) >= limite:
                break
    return resultado


def _cutter_simplificado(sobrenome: str) -> str:
    if len(sobrenome) < 2:
        return "00"
    nome = remover_acentos(sobrenome).upper()
    t2 = {
        "A": "1", "B": "2", "C": "3", "D": "4", "E": "5",
        "F": "6", "G": "7", "H": "8", "I": "8", "J": "9",
        "K": "9", "L": "9", "M": "9", "N": "0", "O": "0",
        "P": "1", "Q": "1", "R": "2", "S": "3", "T": "4",
        "U": "5", "V": "5", "W": "9", "X": "9", "Y": "9", "Z": "9",
    }
    t3 = {
        "A": "1", "B": "3", "C": "5", "D": "6", "E": "7",
        "F": "8", "G": "8", "H": "0", "I": "0", "J": "1",
        "K": "2", "L": "3", "M": "4", "N": "5", "O": "6",
        "P": "7", "Q": "8", "R": "9", "S": "0", "T": "1",
        "U": "2", "V": "3", "W": "4", "X": "5", "Y": "6", "Z": "7",
    }
    return f"{t2.get(nome[1], '0')}{t3.get(nome[2], '0') if len(nome) > 2 else '0'}"


def gerar_codigo_entrada(sobrenome: str, titulo: str = "") -> str:
    if not sobrenome:
        return "XXXX"
    sob = sobrenome.strip().upper()
    vogais = extrair_vogais(sob, 3)
    while len(vogais) < 3:
        vogais += "a"
    letra_titulo = remover_acentos(titulo[0]).lower() if titulo else "x"
    return f"{sob[0]}{_cutter_simplificado(sob)}{letra_titulo}"


def formatar_nome_autor(sobrenome: str, prenomes: str) -> str:
    if not sobrenome and not prenomes:
        return ""
    if not prenomes:
        return f"{sobrenome.upper()}."
    return f"{sobrenome.upper()}, {prenomes.strip()}."


def formatar_nome_apos_barra(sobrenome: str, prenomes: str) -> str:
    if not sobrenome and not prenomes:
        return ""
    if not prenomes:
        return sobrenome.strip()
    return f"{prenomes.strip()} {sobrenome.strip()}"


# ═════════════════════════════════════════════════════════════
# Blocos da ficha
# ═════════════════════════════════════════════════════════════

class FichaCatalografica:
    def __init__(self, dados: dict):
        self.dados = dados

    def _blocos(self) -> list:
        blocos = []
        d = self.dados

        def add(texto, centrado=False, bold=False, direita=False):
            blocos.append((texto, centrado, bold, direita))

        add("Dados Internacionais de Catalogação na Publicação", centrado=True)
        add(d.get("universidade") or "Universidade Federal do Ceará", centrado=True)
        add("Biblioteca Universitária", centrado=True)
        add("")
        add(
            "Gerada automaticamente pelo módulo Catalog, "
            "mediante os dados fornecidos pelo(a) autor(a)",
            centrado=True,
        )
        add("")

        codigo = gerar_codigo_entrada(d.get("autor_sobrenome", ""), d.get("titulo", ""))
        add(codigo)
        add("")

        titulo_completo = d.get("titulo", "")
        if d.get("subtitulo"):
            titulo_completo += f" : {d['subtitulo']}"

        autor_barra = formatar_nome_apos_barra(
            d.get("autor_sobrenome", ""), d.get("autor_prenomes", "")
        )

        if d.get("autor_sobrenome"):
            autor_fmt = formatar_nome_autor(d["autor_sobrenome"], d.get("autor_prenomes", ""))
            add(f"{autor_fmt} {titulo_completo} / {autor_barra}.", bold=True)
        else:
            add(titulo_completo + ".", bold=True)

        editora_str = d.get("editora") or d.get("universidade", "")
        partes = []
        if d.get("edicao"):
            e = d["edicao"] if d["edicao"].endswith(".") else f"{d['edicao']}."
            partes.append(e)
        if d.get("local"):
            if editora_str and d.get("ano"):
                partes.append(f"{d['local']} : {editora_str}, {d['ano']}")
            elif editora_str:
                partes.append(f"{d['local']} : {editora_str}")
            else:
                partes.append(d["local"])
        if partes:
            add(" – " + " – ".join(partes) + ".")

        il = d.get("ilustracoes", "il.").strip()
        if il.lower().startswith("color"):
            il = f"il. {il}"
        elif not il.lower().startswith("il") and not il.lower().startswith("não"):
            il = f"il. {il}"
        il = il.rstrip(".")
        if d.get("paginas"):
            add(f"{d['paginas']} : {il}.")
        else:
            add(f"{il}.")
        add("")

        tipo = d.get("tipo_trabalho", "")
        grau = d.get("grau", "")
        if tipo:
            inicio = f"{tipo} ({grau})" if grau else tipo
            detalhes = [d[k] for k in ("universidade", "centro", "curso", "local", "ano") if d.get(k)]
            if detalhes:
                add(f"{inicio} – {', '.join(detalhes)}.")
            else:
                add(f"{inicio}.")
            add("")

        orient_parts = []
        if d.get("titulo_orientador"):
            orient_parts.append(d["titulo_orientador"])
        if d.get("nome_orientador"):
            orient_parts.append(d["nome_orientador"])
        if orient_parts:
            add(f"Orientação: {' '.join(orient_parts)}.")
        add("")

        assuntos = d.get("assuntos", [])
        if assuntos:
            itens = [f"{i + 1}. {a}." for i, a in enumerate(assuntos)]
            linha = "  ".join(itens)
            if d.get("titulo"):
                linha += "    I. Título."
            add(linha)
        elif d.get("titulo"):
            add("I. Título.")
        add("")

        if d.get("cdd"):
            add(f"CDD {d['cdd']}", direita=True)

        return blocos

    def gerar_texto(self) -> str:
        return "\n".join(b[0] for b in self._blocos())

    def gerar_pdf(self, caminho: str):
        page_w, page_h = A4
        margem_sup = 2.5 * cm
        margem_esq = 2.5 * cm
        margem_dir = 2.5 * cm

        espaco_linha_cabecalho = 0.55 * cm
        espaco_pos_cabecalho = 0.75 * cm
        espaco_pos_cutter = 0.5 * cm
        espaco_entre_blocos = 0.5 * cm
        espaco_desc_fisica_tipo = 0.8 * cm
        espaco_tipo_orientador = 0.6 * cm
        espaco_orientador_assuntos = 0.8 * cm
        espaco_assuntos_cdd = 0.8 * cm
        indentacao = 1.2 * cm

        font_name = "Times-Roman"
        font_bold = "Times-Bold"
        font_size = 11

        c = canvas.Canvas(caminho, pagesize=A4)
        y = page_h - margem_sup

        def draw_text(texto, x=margem_esq, bold=False, right_align=False):
            nonlocal y
            if right_align:
                tw = c.stringWidth(texto, font_bold if bold else font_name, font_size)
                x = page_w - margem_dir - tw
            c.setFont(font_bold if bold else font_name, font_size)
            c.drawString(x, y, texto)
            y -= font_size * 0.42

        def pular(espaco_cm):
            nonlocal y
            y -= espaco_cm

        blocos = self._blocos()
        cdd_texto = None

        # Separar o CDD dos blocos normais
        blocos_render = []
        for b in blocos:
            if b[0].strip().startswith("CDD ") and b[3]:
                cdd_texto = b[0]
            else:
                blocos_render.append(b)

        i = 0
        while i < len(blocos_render):
            texto, centrado, bold, direita = blocos_render[i]

            if not texto.strip():
                anterior = blocos_render[i - 1][0] if i > 0 else ""

                if any(kw in anterior for kw in ["Catalogação", "Biblioteca", "autor(a)"]):
                    pular(espaco_pos_cabecalho)
                elif anterior.strip() and len(anterior.strip()) <= 6:
                    pular(espaco_pos_cutter)
                elif any(kw in anterior.lower() for kw in ["color", "il.", "não il.", "f."]):
                    pular(espaco_desc_fisica_tipo)
                elif any(kw in anterior for kw in ["Conclusão", "Dissertação", "Tese"]):
                    pular(espaco_tipo_orientador)
                elif "Orientação" in anterior:
                    pular(espaco_orientador_assuntos)
                elif "Título" in anterior:
                    pular(espaco_assuntos_cdd)
                else:
                    pular(espaco_entre_blocos)
                i += 1
                continue

            if centrado:
                tw = c.stringWidth(texto, font_name, font_size)
                x_c = (page_w - tw) / 2
                c.setFont(font_bold if bold else font_name, font_size)
                c.drawString(x_c, y, texto)
                y -= font_size * 0.42
                if i + 1 < len(blocos_render) and blocos_render[i + 1][0].strip():
                    pular(espaco_linha_cabecalho - font_size * 0.42)
            else:
                draw_text(texto, x=margem_esq + indentacao, bold=bold)

            if y < 3 * cm:
                c.showPage()
                y = page_h - margem_sup
                c.setFont(font_name, font_size)

            i += 1

        # Renderizar CDD explicitamente
        if cdd_texto:
            y -= espaco_assuntos_cdd
            if y < 3 * cm:
                c.showPage()
                y = page_h - margem_sup
            tw = c.stringWidth(cdd_texto, font_name, font_size)
            x_cdd = page_w - margem_dir - tw
            c.setFont(font_name, font_size)
            c.drawString(x_cdd, y, cdd_texto)

        c.save()


# ═════════════════════════════════════════════════════════════
# Streamlit App
# ═════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Ficha Catalográfica – UFC",
    page_icon="📚",
    layout="wide",
)

injetar_css()

# Header customizado
st.markdown(
    """
    <div class="main-header">
        <h1>📚 Gerador de Ficha Catalográfica</h1>
        <p>Padrão AACR2 + Biblioteca Universitária – Universidade Federal do Ceará</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col_esq, col_dir = st.columns([1, 1])

with col_esq:
    # Seção 1
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">👤 1. Dados do Autor</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    r1c1, r1c2 = st.columns(2)
    autor_sobrenome = r1c1.text_input("Sobrenome", key="autor_sobrenome", placeholder="ex: Silva")
    autor_prenomes = r1c2.text_input("Prenome(s)", key="autor_prenomes", placeholder="ex: João da")

    # Seção 2
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">📖 2. Dados da Obra</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    r2c1, r2c2, r2c3 = st.columns(3)
    titulo = r2c1.text_input("Título", key="titulo", placeholder="ex: Introdução à programação")
    subtitulo = r2c2.text_input("Subtítulo", key="subtitulo", placeholder="ex: um guia prático")
    edicao = r2c3.text_input("Edição", key="edicao", placeholder="ex: 2. ed.")

    # Seção 3
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">📦 3. Publicação</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    r3c1, r3c2, r3c3 = st.columns(3)
    local = r3c1.text_input("Local", key="local", placeholder="ex: Fortaleza")
    editora = r3c2.text_input("Editora/Universidade", key="editora")
    ano = r3c3.text_input("Ano", key="ano", placeholder="ex: 2025")

    # Seção 4
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">📐 4. Descrição Física</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    r4c1, r4c2 = st.columns(2)
    paginas = r4c1.text_input("Folhas/Páginas", key="paginas", placeholder="ex: 85 f.")
    ilustracoes = r4c2.selectbox(
        "Ilustrações",
        ["il.", "il. color.", "il., algumas color.", "não il."],
        key="ilustracoes",
    )

    # Seção 5
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">🎓 5. Trabalho Acadêmico</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    r5c1, r5c2 = st.columns(2)
    tipo_trabalho = r5c1.selectbox(
        "Tipo",
        ["Trabalho de Conclusão de Curso", "Dissertação", "Tese"],
        key="tipo_trabalho",
    )
    grau = r5c2.text_input("Grau", key="grau", placeholder="ex: graduação")

    r5c3, r5c4 = st.columns(2)
    universidade = r5c3.text_input("Universidade", value="Universidade Federal do Ceará", key="universidade")
    centro = r5c4.text_input("Centro/Faculdade", key="centro", placeholder="Opcional")

    r5c5, _ = st.columns(2)
    curso = r5c5.text_input("Curso", key="curso")

    # Seção 6
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">🧑‍🏫 6. Orientador</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    r6c1, r6c2 = st.columns(2)
    titulo_orientador = r6c1.text_input("Título", key="titulo_orientador", placeholder="ex: Prof. Dr.")
    nome_orientador = r6c2.text_input("Nome completo", key="nome_orientador")

    # Seção 7
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">🏷️ 7. Assuntos (até 4)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    r7c1, r7c2 = st.columns(2)
    assunto1 = r7c1.text_input("Assunto 1", key="assunto1")
    assunto2 = r7c2.text_input("Assunto 2", key="assunto2")
    r7c3, r7c4 = st.columns(2)
    assunto3 = r7c3.text_input("Assunto 3", key="assunto3")
    assunto4 = r7c4.text_input("Assunto 4", key="assunto4")

    # Seção 8
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">📊 8. Classificação</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cdd = st.text_input("CDD", key="cdd", placeholder="ex: 005.133")


with col_dir:
    assuntos = [a for a in (assunto1, assunto2, assunto3, assunto4) if a.strip()]

    dados = {
        "autor_sobrenome": autor_sobrenome,
        "autor_prenomes": autor_prenomes,
        "titulo": titulo,
        "subtitulo": subtitulo,
        "edicao": edicao,
        "local": local,
        "editora": editora,
        "ano": ano,
        "paginas": paginas,
        "ilustracoes": ilustracoes,
        "tipo_trabalho": tipo_trabalho,
        "grau": grau,
        "universidade": universidade,
        "centro": centro,
        "curso": curso,
        "titulo_orientador": titulo_orientador,
        "nome_orientador": nome_orientador,
        "assuntos": assuntos,
        "cdd": cdd,
    }

    st.markdown(
        """
        <div class="preview-container">
        """,
        unsafe_allow_html=True,
    )
    st.subheader("👁️ Pré-visualização")

    ficha = FichaCatalografica(dados)
    texto_ficha = ficha.gerar_texto()

    st.text_area("", value=texto_ficha, height=420, disabled=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-card" style="text-align:center;">
            <div class="section-title" style="justify-content:center;">📥 Exportar</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not titulo:
        st.info("Preencha ao menos o **título** para gerar o PDF.")
    else:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, prefix="ficha_") as tmp:
            caminho_tmp = tmp.name

        ficha.gerar_pdf(caminho_tmp)

        with open(caminho_tmp, "rb") as f:
            st.download_button(
                label="⬇️  Baixar PDF",
                data=f.read(),
                file_name="ficha_catalografica.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        try:
            os.unlink(caminho_tmp)
        except Exception:
            pass

# Footer
st.markdown(
    """
    <div class="footer">
        Gerador de Ficha Catalográfica &copy; 2025 — Biblioteca Universitária, UFC
    </div>
    """,
    unsafe_allow_html=True,
)
