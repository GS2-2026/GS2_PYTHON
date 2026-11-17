import json
import os

# ==============================================================================
# 1. TUPLAS (DADOS CONSTANTES E IMUTÁVEIS)
# ==============================================================================
CATEGORIAS_ACOES = (
    "Redução do Consumo de Água",
    "Identificação de Vazamentos",
    "Reutilização de Água",
    "Captação de Água da Chuva",
    "Conscientização sobre uso da Água"
)

STATUS_ACOES = (
    "Pendente",
    "Aprovada",
    "Rejeitada",
    "Sinalizada"
)

NIVEIS_PROGRESSAO = (
    ("Bronze", 0),
    ("Prata", 100),
    ("Ouro", 300),
    ("Diamante", 600),
    ("Esmeralda", 1000)
)

# ==============================================================================
# 2. LISTAS DE DICIONÁRIOS (BASE DE DADOS EM MEMÓRIA)
# ==============================================================================
lista_usuarios = [
    {"id": 1, "nome": "Ana Silva", "pontos": 120, "nivel": "Prata"},
    {"id": 2, "nome": "Carlos Souza", "pontos": 350, "nivel": "Ouro"},
    {"id": 3, "nome": "Beatriz Lima", "pontos": 45, "nivel": "Bronze"}
]

lista_acoes = [
    {
        "id": 1,
        "id_usuario": 1,
        "categoria": "Economia no Banho",
        "descricao": "Redução do tempo de banho",
        "local": "Residência",
        "data": "23/05/2027",
        "pontos": 50,
        "status": "Aprovada"
    },
    {
        "id": 2,
        "id_usuario": 2,
        "categoria": "Identificação de Vazamentos",
        "descricao": "Identificação e comunicação de vazamento",
        "local": "São Paulo - SP",
        "data": "25/05/2027",
        "pontos": 70,
        "status": "Pendente"
    }
    {
        "id": 3,
        "id_usuario": 3,
        "categoria": "Reutilização de Água",
        "descrição": "Reutilização de água para limpeza",
        "local": "São Paulo - SP",
        "data": "30/05/2027",
        "pontos": 45,
        "status": "Aprovada"
    }
]

# função para salvar dados
def salvar_dados():
    dados = {
        "usuarios": lista_usuarios,
        "acoes": lista_acoes
    }

    with open("dados_ecorank.json", "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)

# função para carregar os dados
def carregar_dados():
    global lista_usuarios, lista_acoes

    if os.path.exists("dados_ecorank.json"):
        with open("dados_ecorank.json", "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

            lista_usuarios = dados["usuarios"]
            lista_acoes = dados["acoes"]



# ==============================================================================
# 4. EXPORTAÇÃO DE CONSULTAS PARA JSON
# ==============================================================================

def exportar_dados_para_json(dados, nome_arquivo="exportacao_ecorank.json"):
    """
    Exporta qualquer lista/dicionário do sistema para um arquivo em formato JSON.
    Atende ao requisito de disponibilizar exportação das consultas do CRUD.
    """
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)
        print(
            f"[SUCESSO]: Dados exportados com sucesso para o arquivo '{nome_arquivo}'.")
    except Exception as e:
        print(f"[ERRO]: Falha ao exportar dados para JSON: {e}")

# ==============================================================================
# 5. FUNÇÕES AUXILIARES E REGRAS DE NEGÓCIO
# ==============================================================================


def determinar_nivel(pontos):
    """Recebe os pontos do usuário e retorna o nome do nível alcançado."""
    nivel_atual = "Bronze"
    for item in NIVEIS_PROGRESSAO:
        nome_nivel = item[0]
        pontos_minimos = item[1]
        if pontos >= pontos_minimos:
            nivel_atual = nome_nivel
    return nivel_atual


def buscar_usuario_por_id(id_usuario, usuarios):
    """Busca um usuário na lista pelo seu ID."""
    for usuario in usuarios:
        if usuario["id"] == id_usuario:
            return usuario
    return None


def buscar_acao_por_id(id_acao, acoes):
    """Busca uma ação na lista pelo seu ID."""
    for acao in acoes:
        if acao["id"] == id_acao:
            return acao
    return None


def gerar_novo_id(lista_dados):
    """Gera um novo ID sequencial encontrando o maior ID atual."""
    if len(lista_dados) == 0:
        return 1

    maior_id = 0
    for item in lista_dados:
        if item["id"] > maior_id:
            maior_id = item["id"]

    return maior_id + 1

# ==============================================================================
# 6. FUNÇÕES DE ORGANIZAÇÃO E FILTRAGEM
# ==============================================================================


def filtrar_acoes_por_status(acoes, status_escolhido):
    """Filtra as ações de acordo com o status informado."""
    acoes_filtradas = []
    for acao in acoes:
        if acao["status"].lower() == status_escolhido.lower():
            acoes_filtradas.append(acao)
    return acoes_filtradas


def obter_ranking(usuarios):
    """Ordena a lista de usuários do maior para o menor pontuador."""
    ranking = list(usuarios)
    for i in range(len(ranking)):
        for j in range(i + 1, len(ranking)):
            if ranking[j]["pontos"] > ranking[i]["pontos"]:
                auxiliar = ranking[i]
                ranking[i] = ranking[j]
                ranking[j] = auxiliar
    return ranking

# ==============================================================================
# 7. CRUD DE AÇÕES (COM TRY, EXCEPT, ELSE, FINALLY, API E JSON)
# ==============================================================================


def registrar_acao(acoes, usuarios):
    """Cadastra uma nova ação sustentável no EcoRank Citizen."""
    print("\n--- REGISTRAR NOVA AÇÃO SUSTENTÁVEL ---")

    try:
        id_usuario = int(input("Digite o ID do usuário responsável: "))

        print("\nCategorias disponíveis:")
        posicao = 1

        for cat in CATEGORIAS_ACOES:
            print(f"{posicao} - {cat}")
            posicao = posicao + 1

        opcao_cat = int(input("Escolha o número da categoria (1 a 5): "))

        descricao = input("Descreva a ação realizada: ").strip()
        local = input("Informe o local da ação: ").strip()
        data = input("Informe a data (DD/MM/AAAA): ").strip()

        pontos = int(input("Informe os pontos da ação: "))

    except ValueError:
        print("[ERRO]: Digite números válidos para o ID, categoria e pontos.")

    else:
        usuario = buscar_usuario_por_id(id_usuario, usuarios)

        if usuario is None:
            print(
                f"[AVISO]: Cidadão com ID {id_usuario} não foi encontrado.")
        elif opcao_cat < 1 or opcao_cat > len(CATEGORIAS_ACOES):
            print("[AVISO]: Número de categoria inválido. Escolha de 1 a 5.")
        elif len(descricao) < 5:
            print("[AVISO]: A descrição deve ter pelo menos 5 caracteres.")
        elif len(local) < 3:
            print("[AVISO]: Informe um local válido.")
        elif len(data) != 10:
            print("[AVISO]: Informe a data no formato DD/MM/AAAA.")
        elif pontos <= 0:
            print("[AVISO]: A pontuação deve ser um número maior que zero.")
        else:
            categoria_selecionada = CATEGORIAS_ACOES[opcao_cat - 1]
            novo_id = gerar_novo_id(acoes)

            nova_acao = {
                "id": novo_id,
                "id_usuario": id_usuario,
                "categoria": categoria_selecionada,
                "descricao": descricao,
                "local": local,
                "data": data,
                "pontos": pontos,
                "status": "Pendente"
            }
            acoes.append(nova_acao)
            salvar_dados()

            print(
                f"[SUCESSO]: Ação registrada com ID {novo_id} (Status: Pendente).")
    finally:
        print("[FINALIZAÇÃO]: Processo de registro de ação concluído.")


def listar_acoes(acoes):
    """Exibe todas as ações da lista (Read) e oferece exportação JSON."""
    print("\n--- LISTAGEM DE AÇÕES (READ) ---")
    if len(acoes) == 0:
        print("Nenhuma ação cadastrada.")
        return

    for acao in acoes:
        print(
            f"ID: {acao['id']} | Usuário: {acao['id_usuario']} | Status: {acao['status']} | Pontos: {acao['pontos']}")
        print(f"Categoria: {acao['categoria']}")
        print(f"Descrição: {acao['descricao']}")
        print("-" * 50)

    opcao_exp = input(
        "\nDeseja exportar o resultado dessa consulta para um arquivo JSON? (S/N): ").strip().upper()
    if opcao_exp == "S":
        exportar_dados_para_json(acoes, "consultas_acoes.json")


def atualizar_status_acao(acoes, usuarios):
    """Atualiza o status de uma ação (Update) e bonifica o usuário se aprovada."""
    print("\n--- ATUALIZAR STATUS DE AÇÃO (UPDATE) ---")
    try:
        id_acao = int(input("Digite o ID da ação que deseja alterar: "))

        acao = buscar_acao_por_id(id_acao, acoes)
        if acao is None:
            print(f"[AVISO]: Ação com ID {id_acao} não encontrada.")
            return

        print(f"\nAção ID {acao['id']} - Status Atual: {acao['status']}")
        print("Opções de novo status:")
        posicao = 1
        for st in STATUS_ACOES:
            print(f"{posicao} - {st}")
            posicao = posicao + 1

        opcao_st = int(input("Escolha o novo status (1 a 4): "))

    except ValueError:
        print("[ERRO]: Você deve digitar um número válido.")
    else:
        if opcao_st < 1 or opcao_st > len(STATUS_ACOES):
            print("[AVISO]: Opção de status fora do intervalo (1 a 4).")
        else:
            novo_status = STATUS_ACOES[opcao_st - 1]
            status_antigo = acao["status"]
            acao["status"] = novo_status

            if novo_status == "Aprovada" and status_antigo != "Aprovada":
                usuario = buscar_usuario_por_id(acao["id_usuario"], usuarios)
                if usuario is not None:
                    usuario["pontos"] = usuario["pontos"] + acao["pontos"]
                    usuario["nivel"] = determinar_nivel(usuario["pontos"])
                    print(
                        f"-> Pontos creditados: +{acao['pontos']} para o usuário {usuario['nome']}.")
                    print(f"-> Novo nível do usuário: {usuario['nivel']}.")

            print(
                f"[SUCESSO]: Status da ação ID {id_acao} alterado para '{novo_status}'.")
    finally:
        print("[FINALIZAÇÃO]: Processo de alteração finalizado.")


def excluir_acao(acoes):
    """Remove uma ação da lista pelo seu ID (Delete)."""
    print("\n--- EXCLUIR AÇÃO SUSTENTÁVEL (DELETE) ---")
    try:
        id_acao = int(input("Digite o ID da ação que deseja excluir: "))
    except ValueError:
        print("[ERRO]: O ID deve ser um número inteiro.")
    else:
        acao = buscar_acao_por_id(id_acao, acoes)
        if acao is None:
            print(f"[AVISO]: Ação com ID {id_acao} não encontrada.")
        else:
            confirma = input(
                f"Confirma a exclusão da ação ID {id_acao}? (S/N): ").strip().upper()
            if confirma == "S":
                acoes.remove(acao)
                print(f"[SUCESSO]: Ação ID {id_acao} excluída com sucesso.")
            else:
                print("[AVISO]: Exclusão cancelada.")
    finally:
        print("[FINALIZAÇÃO]: Processo de exclusão finalizado.")

# ==============================================================================
# 8. GESTÃO DE USUÁRIOS
# ==============================================================================


def cadastrar_usuario(usuarios):
    """Cadastra um novo usuário no sistema."""
    print("\n--- CADASTRAR NOVO USUÁRIO ---")
    nome = input("Digite o nome completo do usuário: ").strip()
    if len(nome) < 3:
        print("[AVISO]: O nome deve ter pelo menos 3 caracteres.")
        return

    novo_id = gerar_novo_id(usuarios)
    novo_usuario = {
        "id": novo_id,
        "nome": nome,
        "pontos": 0,
        "nivel": "Bronze"
    }
    usuarios.append(novo_usuario)
    print(
        f"[SUCESSO]: Usuário '{nome}' cadastrado com ID {novo_id} (Nível: Bronze).")


def listar_usuarios(usuarios):
    """Exibe todos os usuários cadastrados e permite exportar para JSON."""
    print("\n--- LISTA DE USUÁRIOS ---")
    if len(usuarios) == 0:
        print("Nenhum usuário cadastrado.")
        return

    for usuario in usuarios:
        print(
            f"ID: {usuario['id']} | Nome: {usuario['nome']} | Pontos: {usuario['pontos']} | Nível: {usuario['nivel']}")

    opcao_exp = input(
        "\nDeseja exportar a lista de usuários para JSON? (S/N): ").strip().upper()
    if opcao_exp == "S":
        exportar_dados_para_json(usuarios, "consultas_usuarios.json")

# ==============================================================================
# 9. MENUS E SUBMENUS COM WHILE E IF/ELIF/ELSE
# ==============================================================================


def submenu_acoes():
    """Submenu para gerenciar o CRUD de ações sustentáveis."""
    executando = True
    while executando:
        print("\n" + "=" * 45)
        print("   SUBMENU - AÇÕES SUSTENTÁVEIS (CRUD)")
        print("=" * 45)
        print("1 - Registrar Nova Ação (Create)")
        print("2 - Listar Todas as Ações (Read)")
        print("3 - Filtrar Ações por Status (Read)")
        print("4 - Validar / Atualizar Status de Ação (Update)")
        print("5 - Excluir Registro de Ação (Delete)")
        print("6 - Exportar Todas as Ações para JSON")
        print("0 - Voltar ao Menu Principal")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            registrar_acao(lista_acoes, lista_usuarios)
        elif opcao == "2":
            listar_acoes(lista_acoes)
        elif opcao == "3":
            print("\nStatus disponíveis:")
            posicao = 1
            for st in STATUS_ACOES:
                print(f"{posicao} - {st}")
                posicao = posicao + 1

            try:
                num_st = int(input("Escolha o número do status: "))
                if 1 <= num_st <= len(STATUS_ACOES):
                    status_escolhido = STATUS_ACOES[num_st - 1]
                    filtradas = filtrar_acoes_por_status(
                        lista_acoes, status_escolhido)
                    listar_acoes(filtradas)
                else:
                    print("[AVISO]: Número de status inválido.")
            except ValueError:
                print("[AVISO]: Digite um valor numérico.")
        elif opcao == "4":
            atualizar_status_acao(lista_acoes, lista_usuarios)
        elif opcao == "5":
            excluir_acao(lista_acoes)
        elif opcao == "6":
            exportar_dados_para_json(lista_acoes, "todas_acoes.json")
        elif opcao == "0":
            executando = False
        else:
            print("[AVISO]: Opção inválida. Digite de 0 a 6.")


def submenu_usuarios():
    """Submenu para gestão de usuários."""
    executando = True
    while executando:
        print("\n" + "=" * 45)
        print("   SUBMENU - GESTÃO DE USUÁRIOS")
        print("=" * 45)
        print("1 - Cadastrar Novo Usuário")
        print("2 - Listar Usuários")
        print("3 - Exportar Usuários para JSON")
        print("0 - Voltar ao Menu Principal")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_usuario(lista_usuarios)
        elif opcao == "2":
            listar_usuarios(lista_usuarios)
        elif opcao == "3":
            exportar_dados_para_json(lista_usuarios, "todos_usuarios.json")
        elif opcao == "0":
            executando = False
        else:
            print("[AVISO]: Opção inválida. Escolha 1, 2, 3 ou 0.")


def submenu_ranking():
    """Submenu para visualizar o ranking e progresso de nível."""
    executando = True
    while executando:
        print("\n" + "=" * 45)
        print("   SUBMENU - RANKING E PROGRESSÃO")
        print("=" * 45)
        print("1 - Visualizar Ranking Geral")
        print("2 - Consultar Progresso Individual")
        print("3 - Exportar Ranking Geral para JSON")
        print("0 - Voltar ao Menu Principal")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            ranking = obter_ranking(lista_usuarios)
            print("\n" + "*" * 40)
            print("       RANKING GERAL ECORANK")
            print("*" * 40)
            posicao = 1
            for usuario in ranking:
                print(
                    f"{posicao}º Lugar: {usuario['nome']} - {usuario['pontos']} pontos ({usuario['nivel']})")
                posicao = posicao + 1
        elif opcao == "2":
            try:
                id_busca = int(input("\nDigite o ID do usuário: "))
                user = buscar_usuario_por_id(id_busca, lista_usuarios)
                if user is not None:
                    print("\n--- FICHA DO USUÁRIO ---")
                    print(f"Nome: {user['nome']}")
                    print(f"Pontuação: {user['pontos']} pontos")
                    print(f"Nível Atual: {user['nivel']}")
                else:
                    print("[AVISO]: Usuário não encontrado.")
            except ValueError:
                print("[AVISO]: O ID deve ser um número inteiro.")
        elif opcao == "3":
            ranking = obter_ranking(lista_usuarios)
            exportar_dados_para_json(ranking, "ranking_ecorank.json")
        elif opcao == "0":
            executando = False
        else:
            print("[AVISO]: Opção inválida. Escolha 1, 2, 3 ou 0.")


def relatorio_impacto(acoes):

    print("\n" + "=" * 45)
    print("       RELATORIO DE IMPACTO COMUNITARIO")
    print("\n" + "=" * 45)

    total_acoes = len(acoes)

    aprovadas = 0
    pendentes = 0
    rejeitadas = 0
    sinalizadas = 0

    pontos_distribuidos = 0

    for acao in acoes:

        if acao["status"] == "Aprovada":
            aprovadas = aprovadas + 1
            pontos_distribuidos = pontos_distribuidos + acao["pontos"]

        elif acao["status"] == "Pendente":
            pendentes = pendentes + 1

        elif acao["status"] == "Sinalizada":
            sinalizadas = sinalizadas + 1

        elif acao["status"] == "Rejeitada":
            rejeitadas = rejeitadas + 1

        else:
            sinalizadas = sinalizadas + 1

    print(f"\nTotal de ações: {total_acoes}")
    print(f"Ações aprovada: {aprovadas}")
    print(f"Ações pendentes: {pendentes}")
    print(f"Ações rejeitadas: {rejeitadas}")
    print(f"Ações sinalizadas: {sinalizadas}")

    print(f"\nTotal de pontos distribuidos: {pontos_distribuidos}")

    print("=" * 45)


def menu_principal():
    """Menu principal do sistema."""
    executando = True
    while executando:
        print("\n" + "=" * 55)
        print("   ECORANK - GAMIFICAÇÃO SUSTENTÁVEL (SOULUP) - SPRINT 4")
        print("=" * 55)
        print("1 - Gestão de ações sustentáveis")
        print("2 - Gestão de Cidadãos")
        print("3 - Ranking e Progressão")
        print("4 - Relatório de impacto comunitário")
        print("0 - Sair do Sistema")
        print("=" * 55)

        opcao = input("Digite a opção desejada: ").strip()

        match opcao:

            case "1":
                submenu_acoes()

            case "2":
                submenu_usuarios()

            case"3":
                submenu_ranking()

            case"4":
                relatorio_impacto(lista_acoes)

            case"0":
                print("\nSaindo do Sistema.")
                executando = False


if __name__ == "__main__":
    menu_principal()
    carregar_dados()
    salvar_dados()
