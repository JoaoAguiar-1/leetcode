import sys
import os
import requests
import time

# Força o terminal a usar UTF-8 (permite imprimir emojis no Windows)
sys.stdout.reconfigure(encoding='utf-8')

def estruturar_lista_leetcode(nome_lista):
    """
    Busca os exercícios de uma lista do LeetCode, cria a estrutura 
    de pastas e salva as descrições e arquivos de solução em branco.
    """
    
    print(f"[{nome_lista}] Iniciando estruturação da lista...")
    
    # ==========================================
    # 1. CRIAR A ESTRUTURA DE PASTAS
    # ==========================================
    pasta_base = "quests"
    
    pasta_descricoes = os.path.join(pasta_base, nome_lista, "descricoes")
    pasta_solucoes = os.path.join(pasta_base, nome_lista, "solucoes")
    
    # exist_ok=True faz com que não dê erro se a pasta já existir
    os.makedirs(pasta_descricoes, exist_ok=True)
    os.makedirs(pasta_solucoes, exist_ok=True)
    
    print(f" Pastas preparadas: '{pasta_descricoes}/' e '{pasta_solucoes}/'")

    # ==========================================
    # 2. PEGAR A LISTA DE PROBLEMAS DO PLANO
    # ==========================================
    url_graphql = "https://leetcode.com/graphql"

    query_plano = """
    query studyPlanV2Detail($slug: String!) {
      studyPlanV2Detail(planSlug: $slug) {
        planSubGroups {
          questions {
            titleSlug
          }
        }
      }
    }
    """

    resposta_plano = requests.post(
        url_graphql, 
        json={
            "query": query_plano, 
            "variables": {"slug": nome_lista}
        },
        headers={"User-Agent": "Mozilla/5.0"} 
    )

    dados_plano = resposta_plano.json()
    
    # Validar se a lista existe
    if not dados_plano.get("data") or not dados_plano["data"].get("studyPlanV2Detail"):
        print(f"❌ Erro: Não foi possível encontrar a lista '{nome_lista}'. Verifique o nome.")
        return

    lista_de_slugs = []
    subgrupos = dados_plano["data"]["studyPlanV2Detail"]["planSubGroups"]

    for grupo in subgrupos:
        for questao in grupo["questions"]:
            lista_de_slugs.append(questao["titleSlug"])

    print(f"✅ Encontrados {len(lista_de_slugs)} problemas. Verificando arquivos...\n")


    # ==========================================
    # 3. BAIXAR DESCRIÇÕES E CRIAR SOLUÇÕES
    # ==========================================
    query_questao = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionFrontendId
        title
        content
      }
    }
    """
    # Lemos os arquivos que já existem na pasta para não baixar de novo
    arquivos_existentes = os.listdir(pasta_solucoes)
    
    # enumerate(..., start=1) nos dá um contador automático (1, 2, 3...)
    for ordem, slug in enumerate(lista_de_slugs, start=1):
        
        # Transforma o 1 em "00001", o 2 em "00002" e etc.
        ordem_formatada = f"{ordem:05d}"
        
        # Checa se algum arquivo na pasta de soluções termina com o nome do problema
        ja_baixado = any(arq.endswith(f"{slug}.py") for arq in arquivos_existentes)

        if ja_baixado:
            # Se já existir, pula para o próximo exercício sem avisar, para ser rápido
            continue
            
        print(f"  [{ordem_formatada}] Baixando: {slug}...")
        
        resposta_questao = requests.post(
            url_graphql, 
            json={"query": query_questao, "variables": {"titleSlug": slug}},
            headers={"User-Agent": "Mozilla/5.0"}
        )
        
        dados_questao = resposta_questao.json()
        
        if dados_questao.get('data') and dados_questao['data'].get('question'):
            dados = dados_questao['data']['question']
            titulo = dados['title']
            conteudo_html = dados['content']
            id_leetcode = dados['questionFrontendId'] # Pegamos o "88"
            
            # Monta o novo nome do arquivo: 00001_88_merge-sorted-array
            nome_arquivo_base = f"{ordem_formatada}_{id_leetcode}_{slug}"
            
            caminho_descricao = os.path.join(pasta_descricoes, f"{nome_arquivo_base}.md")
            caminho_solucao = os.path.join(pasta_solucoes, f"{nome_arquivo_base}.py")
            
            # 3.1 Criar o arquivo de solução em branco
            with open(caminho_solucao, "w", encoding="utf-8") as f_sol:
                f_sol.write(f"# {id_leetcode}. {titulo}\n\n")
                pass 
                
            # 3.2 Salvar o arquivo de descrição
            with open(caminho_descricao, "w", encoding="utf-8") as f_desc:
                f_desc.write(f"# {id_leetcode}. {titulo}\n")
                if conteudo_html: 
                    f_desc.write(conteudo_html)
                else:
                    f_desc.write("<p><i>Conteúdo não disponível ou exclusivo para contas Premium.</i></p>")
            
            print(f"  -> Salvo: {nome_arquivo_base}")
        else:
            print(f"  [ERRO] Erro ao baixar a descrição de '{slug}'.")
        
        # Espera 2 segundos para respeitar os limites do servidor do LeetCode
        time.sleep(2)
    

    print(f"\n🚀 Estruturação da lista '{nome_lista}' finalizada com sucesso!")

# ==========================================
# EXECUTANDO A FUNÇÃO
# ==========================================
if __name__ == "__main__":
    # Você pode chamar a função passando qualquer "slug" válido do LeetCode
    estruturar_lista_leetcode("top-interview-150")