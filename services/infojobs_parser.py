"""
Parser otimizado para InfoJobs - ZERO BeautifulSoup.
Usa apenas: httpx + regex + json (stdlib)
Extrai dados do JSON-LD (schema.org JobPosting) + regex mínimo no HTML.
"""

import re
import json
import html as html_mod
import httpx
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict, field


INFOJOBS_URL = "https://www.infojobs.com.br/vacancydetail.aspx"
INFOJOBS_EMPRESA_URL = "https://www.infojobs.com.br/detailvacancy/about.aspx"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


@dataclass
class EmpresaDetalhes:
    """Dados da empresa extraídos da aba 'Empresa'"""
    nome: str = ""
    descricao: str = ""
    setor: str = ""
    porte: str = ""
    matriz: str = ""
    url: str = ""


@dataclass
class FonteMetadados:
    """Metadados da fonte de coleta"""
    portal: str = "infojobs"
    id_externo: str = ""
    url_original: str = ""
    data_coleta: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class VagaInfoJobs:
    """Dados extraídos da vaga do InfoJobs"""
    id_vaga: str
    titulo: str
    empresa: str  # nível superior para mapeamento direto
    empresa_detalhes: EmpresaDetalhes
    link: str
    salario_bruto: str  # "Salário a combinar" ou "R$ 5.000 a R$ 8.000"
    salario_min: Optional[float] = None
    salario_max: Optional[float] = None
    modalidade: str = ""  # "Remoto", "Presencial", "Híbrido"
    localizacao: str = ""  # "Curitiba - PR"
    cidade: str = ""
    estado: str = ""
    descricao: str = ""
    tipo_contrato: str = ""  # "Tempo parcial", "Tempo integral", etc.
    data_publicacao: str = ""  # ISO format
    data_validade: str = ""
    requisitos: list[str] = field(default_factory=list)
    beneficios: list[str] = field(default_factory=list)
    habilidades: list[str] = field(default_factory=list)
    adequacao_media: str = ""
    fonte: FonteMetadados = field(default_factory=FonteMetadados)


def _extrair_json_ld(html: str) -> Optional[dict]:
    """Extrai o JSON-LD do schema.org JobPosting"""
    match = re.search(
        r'<script type="application/ld\+json">\s*(\{[\s\S]*?\})\s*</script>',
        html
    )
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _extrair_titulo_html(html: str) -> Optional[str]:
    """Extrai o título completo do <h2 class="js_vacancyHeaderTitle">"""
    match = re.search(
        r'<h2[^>]*class="[^"]*\bjs_vacancyHeaderTitle\b[^"]*"[^>]*>([^<]+)</h2>',
        html
    )
    if match:
        return html_mod.unescape(match.group(1).strip())
    return None


def _extrair_modalidade(html: str) -> str:
    """Extrai modalidade (Remoto/Presencial/Híbrido) dentro do VacancyHeader"""
    # Buscar apenas no bloco VacancyHeader para evitar vagas similares
    idx = html.find('VacancyHeader')
    if idx < 0:
        idx = 0
    header_section = html[idx:idx+5000]
    
    # Padrão 1: ícone house-and-building + texto (Híbrido)
    match = re.search(
        r'icon-(?:house-and-building|buildings)[^>]*>.*?</svg>\s*([^\n<]+)',
        header_section,
        re.IGNORECASE | re.DOTALL
    )
    if match:
        return html_mod.unescape(match.group(1).strip())
    # Fallback: página toda
    for modo in ("Remoto", "Presencial", "Híbrido", "Hibrido"):
        if re.search(rf'icon-(?:house-and-building|buildings)[^>]*>.*?{modo}', html[:idx+5000] if idx > 0 else html, re.IGNORECASE | re.DOTALL):
            return modo
    return "Não informado"


def _extrair_salario(html: str) -> str:
    """Extrai salário do HTML - busca o 2º div.text-medium.mb-4 (que é o salário)"""
    # Encontra todos os divs text-medium mb-4
    matches = list(re.finditer(
        r'<div class="text-medium mb-4"[^>]*>\s*([\s\S]*?)\s*</div>',
        html,
        re.IGNORECASE
    ))
    # O 2º div.text-medium.mb-4 é SEMPRE o salário (1º = localização, 2º = salário)
    if len(matches) >= 2:
        value = matches[1].group(1).strip()
        # Limpar HTML residual e múltiplas quebras
        value = re.sub(r'<[^>]+>', '', value)
        value = re.sub(r'\s+', ' ', value).strip()
        if value:
            return html_mod.unescape(value)
    # Fallback: procurar na página toda
    match = re.search(r'(Sal[aá]rio\s*a\s*combinar|R\$\s*[\d.,]+\s*(?:Bruto|a\s*R\$|mensal)?)', html, re.IGNORECASE)
    if match:
        return html_mod.unescape(match.group(1).strip())
    return "Não informado"


def _extrair_lista_secao(html: str, secao_titulo: str) -> list[str]:
    """
    Extrai lista de uma seção (Exigências, Valorizado, Habilidades, Benefícios).
    Padrão: <div class="h4 font-weight-bold text-body mb-12">Exigências</div>
            <div class="mb-32"><ul class="custom-list"><li>Item 1</li>...</ul></div>
    """
    # Escapa o título para regex
    titulo_esc = re.escape(secao_titulo)
    # Procura o título seguido de lista <ul class="custom-list"> com <li>
    padrao = (
        rf'<div class="h4 font-weight-bold text-body mb-12"[^>]*>\s*{titulo_esc}\s*</div>'
        r'\s*<div class="mb-32">\s*'
        r'<ul class="custom-list">(.*?)</ul>'
    )
    match = re.search(padrao, html, re.IGNORECASE | re.DOTALL)
    if not match:
        return []
    
    lista_html = match.group(1)
    # Extrair cada <li>...conteúdo...</li>
    itens = re.findall(r'<li>\s*([^<]+)\s*</li>', lista_html)
    return [html_mod.unescape(item.strip()) for item in itens if item.strip()]


def _extrair_habilidades(html: str) -> list[str]:
    """Extrai habilidades/tags do formato <div class="tag ..."><span>texto</span></div>"""
    padrao = r'<div class="tag[^"]*"[^>]*>\s*<span>\s*([^<]+)\s*</span>'
    matches = re.findall(padrao, html)
    return [m.strip() for m in matches if m.strip()]


def _extrair_empresa_url(html: str, empresa_nome: str) -> str:
    """Extrai URL da empresa a partir do nome no VacancyHeader"""
    # Estratégia: encontrar links no bloco VacancyHeader que tenham o nome da empresa
    
    # 1. Procurar primeiro no VacancyHeader (seção mais confiável)
    idx_header = html.find('VacancyHeader')
    if idx_header > 0:
        header = html[idx_header:idx_header+3000]
        
        # Padrão 1a: target="_blank" com href (formato: empresa-nome__id.aspx)
        match = re.search(
            r'href="(https?://www\.infojobs\.com\.br/empresa-[^"]+)"',
            header
        )
        if match:
            return match.group(1)
        
        # Padrão 1b: class="mr-4 text-decoration-none" (formato: /nome-da-empresa)
        match = re.search(
            r'<a[^>]*class="[^"]*\bmr-4\b[^"]*text-decoration-none[^"]*"[^>]*href="([^"]+)"',
            header
        )
        if match:
            url = match.group(1)
            if url.startswith("http"):
                return url
            if url.startswith("/"):
                return f"https://www.infojobs.com.br{url}"
    
    # 2. Fallback: buscar na página toda por href que contenha o nome da empresa
    # Sanitizar nome: remover acentos, ç, etc para matching flexível
    def sanitize(s):
        return re.sub(r'[^a-z0-9]', '', s.lower().replace('ç', 'c').replace('á', 'a').replace('é', 'e')
                       .replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ã', 'a').replace('õ', 'o'))
    
    nome_clean = sanitize(empresa_nome)
    if len(nome_clean) >= 4:
        # Procurar qualquer href que contenha pelo menos 4 chars consecutivos do nome
        for i in range(len(nome_clean) - 3):
            chunk = nome_clean[i:i+4]
            match = re.search(
                rf'href="(https?://www\.infojobs\.com\.br/[^"]*{re.escape(chunk)}[^"]*)"',
                html,
                re.IGNORECASE
            )
            if match:
                return match.group(1)
    
    return ""


def _extrair_empresa_detalhes(html: str, empresa_nome: str) -> EmpresaDetalhes:
    """Extrai dados da empresa da aba 'Empresa' (detailvacancy/about.aspx)"""
    detalhes = EmpresaDetalhes(nome=empresa_nome)
    
    # Descrição da empresa - primeira div mb-16 white-space-pre-line
    match = re.search(
        r'class="mb-16 white-space-pre-line"[^>]*>([^<]+)</div>',
        html
    )
    if match:
        detalhes.descricao = match.group(1).strip()
    
    # Setor: <span class="font-weight-bold">Setor: </span>TI
    match = re.search(r'font-weight-bold">\s*Setor:\s*</span>\s*([^<\n]+)', html)
    if match:
        detalhes.setor = match.group(1).strip()
    
    # Porte/Funcionários: <span class="font-weight-bold">Funcionários: </span>Micro empresa...
    match = re.search(r'font-weight-bold">\s*Funcion[áa]rios:\s*</span>\s*([^<\n]+)', html)
    if match:
        detalhes.porte = match.group(1).strip()
    
    # Matriz: <span class="font-weight-bold">Matriz: </span>Santa Catarina
    match = re.search(r'font-weight-bold">\s*Matriz:\s*</span>\s*([^<\n]+)', html)
    if match:
        detalhes.matriz = match.group(1).strip()
    
    # URL da empresa (primeira ocorrência)
    detalhes.url = _extrair_empresa_url(html, empresa_nome)
    
    return detalhes


def _extrair_habilidades(html: str) -> list[str]:
    """Extrai habilidades/tags do formato <div class="tag ..."><span>texto</span></div>
    Filtra ruído como "NOVA" que aparece em vagas similares"""
    padrao = r'<div class="tag[^"]*"[^>]*>\s*<span>\s*([^<]+)\s*</span>'
    matches = re.findall(padrao, html)
    habilidades = [html_mod.unescape(m.strip()) for m in matches if m.strip()]
    # Filtrar ruído conhecido (decodificado)
    ruido = {"nova", "new", "urgente", "destaque", "contratação urgente", "contratacao urgente"}
    return [h for h in habilidades if h.lower().strip() not in ruido]


def _extrair_adequacao_media(html: str) -> str:
    """Extrai adequação média dos inscritos da aba 'Comparativo'"""
    match = re.search(r'A adequação média para os candidatos inscritos é de\s*<span[^>]*>([^<]+)</span>', html)
    if match:
        return match.group(1).strip()
    return ""


def parse_vaga_infojobs(vaga_id: str) -> Optional[VagaInfoJobs]:
    """
    Função principal: busca e parseia uma vaga do InfoJobs pelo ID.
    Faz 2 requests paralelos: vaga principal + aba Empresa.
    Retorna VagaInfoJobs ou None se falhar.
    """
    import asyncio
    
    params = {"iv": vaga_id, "originmatch": "10"}
    
    async def _buscar_tudo():
        async with httpx.AsyncClient(timeout=30.0, headers=HEADERS, follow_redirects=True) as client:
            # Requests paralelos
            tarefa_vaga = client.get(INFOJOBS_URL, params=params)
            tarefa_empresa = client.get(INFOJOBS_EMPRESA_URL, params={"iv": vaga_id})
            
            resp_vaga, resp_empresa = await asyncio.gather(tarefa_vaga, tarefa_empresa)
            
        resp_vaga.raise_for_status()
        resp_empresa.raise_for_status()
        
        return resp_vaga.text, resp_empresa.text
    
    # Executa asyncio
    try:
        html_vaga, html_empresa = asyncio.run(_buscar_tudo())
    except httpx.HTTPError as e:
        print(f"[Erro HTTP] {e}")
        return None
    
    # 1. JSON-LD (dados estruturados principais)
    json_ld = _extrair_json_ld(html_vaga)
    if not json_ld:
        print("[Erro] JSON-LD não encontrado")
        return None
    
    # 1b. Título do HTML (mais completo que JSON-LD)
    titulo_html = _extrair_titulo_html(html_vaga)
    titulo = titulo_html or json_ld.get("title", "")
    
    # 2. Dados complementares via regex mínimo
    modalidade = _extrair_modalidade(html_vaga)
    salario_bruto = _extrair_salario(html_vaga)
    requisitos = _extrair_lista_secao(html_vaga, "Exigências")
    valorizado = _extrair_lista_secao(html_vaga, "Valorizado")
    beneficios = _extrair_lista_secao(html_vaga, "Benefícios")
    habilidades = _extrair_habilidades(html_vaga)
    
    # 3. Dados da empresa (aba Empresa)
    empresa_nome = json_ld.get("hiringOrganization", {}).get("name", "")
    empresa_detalhes = _extrair_empresa_detalhes(html_empresa, empresa_nome)
    
    # 4. Adequação média (aba Comparativo) - opcional, buscar se precisar
    adequacao_media = ""
    
    # Combinar requisitos + valorizado
    todos_requisitos = requisitos + valorizado
    
    # Localização do JSON-LD
    loc = json_ld.get("jobLocation", {}).get("address", {})
    cidade = loc.get("addressLocality", "")
    estado = loc.get("addressRegion", "")
    localizacao = f"{cidade} - {estado}".strip(" -")
    
    # Link canônico
    link = f"{INFOJOBS_URL}?iv={vaga_id}&originmatch=10"
    
    # Parse salário: priorizar baseSalary do JSON-LD
    salario_min, salario_max = _parse_salario(salario_bruto, json_ld)
    
    # Descrição decodificada
    descricao = html_mod.unescape(json_ld.get("description", ""))
    
    return VagaInfoJobs(
        id_vaga=vaga_id,
        titulo=titulo,
        empresa=empresa_nome,
        empresa_detalhes=empresa_detalhes,
        link=link,
        salario_bruto=salario_bruto,
        salario_min=salario_min,
        salario_max=salario_max,
        modalidade=modalidade,
        localizacao=localizacao,
        cidade=cidade,
        estado=estado,
        descricao=descricao,
        tipo_contrato=json_ld.get("employmentType", ""),
        data_publicacao=json_ld.get("datePosted", ""),
        data_validade=json_ld.get("validThrough", ""),
        requisitos=todos_requisitos,
        beneficios=beneficios,
        habilidades=habilidades,
        adequacao_media=adequacao_media,
        fonte=FonteMetadados(
            id_externo=vaga_id,
            url_original=link,
        ),
    )


def _parse_salario(salario_bruto: str, json_ld: Optional[dict] = None) -> tuple[Optional[float], Optional[float]]:
    """
    Extrai salario_min e salario_max.
    Prioridade: JSON-LD baseSalary > regex no texto HTML.
    """
    # 1. Tentar baseSalary do JSON-LD (mais confiável)
    if json_ld:
        bs = json_ld.get("baseSalary") or {}
        val = bs.get("value") or {}
        if isinstance(val, dict):
            min_v = val.get("minValue")
            max_v = val.get("maxValue")
            if min_v is not None:
                return float(min_v), float(max_v) if max_v is not None else None
    
    # 2. Fallback: regex no texto HTML
    # Padrão: R$ 5.000 a R$ 8.000  ou  R$ 5.000,00 a R$ 8.000,00
    match = re.search(r'R\$\s*([\d.,]+)\s*a\s*R\$\s*([\d.,]+)', salario_bruto)
    if match:
        try:
            min_val = float(match.group(1).replace(".", "").replace(",", "."))
            max_val = float(match.group(2).replace(".", "").replace(",", "."))
            return min_val, max_val
        except ValueError:
            pass
    # Padrão: R$ 5.000 (fixo)
    match = re.search(r'R\$\s*([\d.,]+)', salario_bruto)
    if match:
        try:
            val = float(match.group(1).replace(".", "").replace(",", "."))
            return val, None
        except ValueError:
            pass
    return None, None


def parse_vaga_infojobs_dict(vaga_id: str) -> Optional[dict]:
    """Wrapper que retorna dict completo (compatível com seu modelo + extras)"""
    vaga = parse_vaga_infojobs(vaga_id)
    if vaga is None:
        return None
    
    d = asdict(vaga)
    # Mapear para campos do seu modelo `criar_vaga` + extras organizados
    return {
        # Campos diretos do modelo criar_vaga
        "nome": d["titulo"],
        "empresa": d["empresa"],
        "link": d["link"],
        "salario": d["salario_min"],
        "salario_max": d["salario_max"],
        "modalidade": d["modalidade"],
        "descricao": d["descricao"],
        "interesse": 3,
        "aderencia": 3,
        "status": "Interessado",
        "portal_id": None,  # será preenchido pelo portal selecionado
        "data_encontrada": "",  # será preenchida no callback com a data de hoje
        "data_envio": "",
        "data_publicacao": d["data_publicacao"][:10] if d["data_publicacao"] else "",
        "fonte_id": d["id_vaga"],
        "notas": (
            f"📌 InfoJobs (ID: {d['id_vaga']})\n"
            f"📅 Publicada: {d['data_publicacao'][:10] if d['data_publicacao'] else '—'}\n"
            f"⏳ Válida até: {d['data_validade'][:10] if d['data_validade'] else '—'}\n"
            f"📍 Local: {d['localizacao'] or '—'}\n"
            f"📋 Tipo: {d['tipo_contrato'] or '—'}\n"
        ),
        "tag_ids": None,
        
        # Extras organizados (não vão pro banco, mas úteis pro front/debug)
        "extras": {
            "empresa_detalhes": d["empresa_detalhes"],
            "localizacao_detalhada": {
                "cidade": d["cidade"],
                "estado": d["estado"],
                "completa": d["localizacao"]
            },
            "salario_bruto": d["salario_bruto"],
            "tipo_contrato": d["tipo_contrato"],
            "data_publicacao": d["data_publicacao"],
            "data_validade": d["data_validade"],
            "requisitos": d["requisitos"],
            "beneficios": d["beneficios"],
            "habilidades": d["habilidades"],
            "adequacao_media": d["adequacao_media"],
            "fonte": d["fonte"],
        }
    }


# ─── Teste rápido ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    test_id = sys.argv[1] if len(sys.argv) > 1 else "11616056"
    print(f"🔍 Buscando vaga InfoJobs ID: {test_id}...")
    resultado = parse_vaga_infojobs_dict(test_id)
    if resultado:
        print("\n✅ DADOS EXTRAÍDOS:")
        for k, v in resultado.items():
            if isinstance(v, list):
                print(f"  {k}: {v}")
            elif isinstance(v, str) and len(v) > 200:
                print(f"  {k}: {v[:200]}...")
            else:
                print(f"  {k}: {v}")
    else:
        print("❌ Falha ao extrair vaga")