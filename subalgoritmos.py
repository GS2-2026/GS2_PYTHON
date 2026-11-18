"""Subalgoritmos: cadastros, validações, cálculos e arquivos do EcoComunidade."""
import json
import os
from datetime import datetime, date

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = os.path.join(PASTA, 'dados', 'agua.json')


# Leitura e gravação dos arquivos
def carregar_dados():
    if not os.path.exists(ARQUIVO):
        return {'residencias': [], 'hidrometros': [], 'leituras': []}
    with open(ARQUIVO, 'r', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)
    validar_dados(dados)
    return dados


def validar_dados(dados):
    """Recusa arquivos inconsistentes antes que seus registros cheguem aos menus."""
    if not isinstance(dados, dict):
        raise ValueError('Os dados devem ser um dicionário.')
    ids = {}
    for chave in ('residencias', 'hidrometros', 'leituras'):
        if not isinstance(dados.get(chave), list):
            raise ValueError('Estrutura do arquivo inválida.')
        ids[chave] = set()
        for registro in dados[chave]:
            if not isinstance(registro, dict):
                raise ValueError('Registro inválido.')
            identificador = registro.get('id')
            if type(identificador) is not int or identificador <= 0 or identificador in ids[chave]:
                raise ValueError('ID inválido ou repetido.')
            ids[chave].add(identificador)

    for residencia in dados['residencias']:
        for campo in ('descricao', 'comunidade'):
            if not isinstance(residencia.get(campo), str) or not residencia[campo].strip():
                raise ValueError('Texto da residência inválido.')

    residencias_vinculadas = set()
    nomes = set()
    for medidor in dados['hidrometros']:
        vinculo = medidor.get('id_residencia')
        if type(vinculo) is not int or vinculo not in ids['residencias'] or vinculo in residencias_vinculadas:
            raise ValueError('Vínculo do hidrômetro inválido ou repetido.')
        residencias_vinculadas.add(vinculo)
        nome = medidor.get('identificacao')
        if not isinstance(nome, str) or not nome.strip() or nome.strip().casefold() in nomes:
            raise ValueError('Identificação do hidrômetro inválida ou repetida.')
        nomes.add(nome.strip().casefold())
        validar_numero_salvo(medidor.get('limite_diario_m3'), positivo=True)

    for leitura in dados['leituras']:
        vinculo = leitura.get('id_hidrometro')
        if type(vinculo) is not int or vinculo not in ids['hidrometros']:
            raise ValueError('Leitura sem hidrômetro válido.')
        texto_data = leitura.get('data')
        if not isinstance(texto_data, str):
            raise ValueError('Data inválida.')
        data_leitura = date.fromisoformat(texto_data)
        if texto_data != data_leitura.isoformat() or data_leitura > date.today():
            raise ValueError('Data inválida ou futura.')
        validar_numero_salvo(leitura.get('valor_m3'))

    for medidor in dados['hidrometros']:
        leituras = obter_leituras(dados, medidor['id'])
        for indice in range(1, len(leituras)):
            anterior, atual = leituras[indice - 1], leituras[indice]
            if anterior['data'] == atual['data'] or anterior['valor_m3'] > atual['valor_m3']:
                raise ValueError('Leituras repetidas ou consumo decrescente.')


def validar_numero_salvo(valor, positivo=False):
    if type(valor) not in (int, float):
        raise ValueError('Valor numérico inválido.')
    try:
        # A comparação também recusa infinito e valores indefinidos (NaN).
        finito = float('-inf') < float(valor) < float('inf')
    except OverflowError:
        finito = False
    if not finito or valor < 0 or (positivo and valor == 0):
        raise ValueError('Valor numérico fora do intervalo permitido.')


def salvar_dados(dados):
    # Gravar primeiro uma cópia evita perder o arquivo anterior se a gravação falhar.
    os.makedirs(os.path.dirname(ARQUIVO), exist_ok=True)
    temporario = ARQUIVO + '.tmp'
    with open(temporario, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)
    os.replace(temporario, ARQUIVO)


# Validação das entradas do usuário
def ler_texto(mensagem):
    while True:
        texto = input(mensagem).strip()
        if texto:
            return texto
        print('Preencha o campo.')


def ler_numero(mensagem, positivo=False):
    while True:
        try:
            numero = float(input(mensagem).strip().replace(',', '.'))
            if not (0 <= numero < float('inf')):
                print('Informe um número finito, maior ou igual a zero.')
            elif positivo and numero == 0:
                print('O limite deve ser maior que zero.')
            else:
                return numero
        except ValueError:
            print('Digite um número. Pode usar ponto ou vírgula decimal.')


def ler_data():
    while True:
        try:
            valor = datetime.strptime(input('Data (DD/MM/AAAA): '), '%d/%m/%Y').date()
            if valor > date.today():
                print('A data não pode estar no futuro.')
            else:
                return valor.isoformat()
        except ValueError:
            print('Data inválida. Exemplo: 01/11/2026.')


# Busca e identificação dos cadastros
def proximo_id(registros):
    maior = 0
    for registro in registros:
        if registro['id'] > maior:
            maior = registro['id']
    return maior + 1


def escolher(registros):
    if not registros:
        print('Nenhum cadastro disponível.')
        return None
    for registro in registros:
        if "descricao" in registro:
            nome = registro["descricao"]
        else:
            nome = registro["identificacao"]
        print(f"{registro['id']} - {nome}")
    while True:
        escolha = input('Informe o ID (0 para voltar): ').strip()
        if escolha == '0':
            return None
        for registro in registros:
            if escolha == str(registro['id']):
                return registro
        print('ID inexistente. Tente novamente.')


# Cadastro de residências e hidrômetros
def menu_cadastros(dados):
    while True:
        print('\nCADASTROS\n1 - Cadastrar residência\n2 - Listar residências\n3 - Cadastrar hidrômetro\n4 - Listar hidrômetros\n5 - Alterar limite\n6 - Excluir residência\n7 - Excluir hidrômetro\n0 - Voltar')
        match input('Opção: ').strip():
            case '1':
                residencia = {'id': proximo_id(dados['residencias']),
                              'descricao': ler_texto('Descrição da residência: '),
                              'comunidade': ler_texto('Comunidade: ')}
                dados['residencias'].append(residencia)
                salvar_dados(dados)
                print('Residência salva.')
            case '2':
                comunidades = set()
                for residencia in dados['residencias']:
                    print(f"{residencia['id']} - {residencia['descricao']} | {residencia['comunidade']}")
                    comunidades.add(residencia['comunidade'])
                print(f'Total de comunidades diferentes: {len(comunidades)}')
            case '3':
                residencia = escolher(dados['residencias'])
                if residencia is None:
                    continue
                existe = False
                for medidor in dados['hidrometros']:
                    if medidor['id_residencia'] == residencia['id']:
                        existe = True
                if existe:
                    print('Esta versão aceita um hidrômetro por residência.')
                    continue
                nome = ler_texto('Identificação do hidrômetro: ')
                for medidor in dados['hidrometros']:
                    if medidor['identificacao'].casefold() == nome.casefold():
                        existe = True
                if existe:
                    print('Identificação já utilizada.')
                    continue
                limite = ler_numero('Limite demonstrativo em m³/dia (definido pelo usuário): ', True)
                dados['hidrometros'].append({'id': proximo_id(dados['hidrometros']), 'id_residencia': residencia['id'], 'identificacao': nome, 'limite_diario_m3': limite})
                salvar_dados(dados)
                print('Hidrômetro salvo.')
            case '4':
                if not dados['hidrometros']:
                    print('Nenhum hidrômetro cadastrado.')
                for medidor in dados['hidrometros']:
                    print(f"{medidor['id']} - {medidor['identificacao']} | Residência {medidor['id_residencia']} | Limite {medidor['limite_diario_m3']:.3f} m³/dia")
            case '5':
                medidor = escolher(dados['hidrometros'])
                if medidor is not None:
                    medidor['limite_diario_m3'] = ler_numero('Novo limite em m³/dia: ', True)
                    salvar_dados(dados)
                    print('Limite salvo. As consultas anteriores usarão este novo limite.')
            case '6':
                excluir_cadastro(dados, 'residencias')
            case '7':
                excluir_cadastro(dados, 'hidrometros')
            case '0':
                return
            case _:
                print('Opção inválida.')


# Organização das leituras e cálculos
def chave_data(leitura):
    return leitura['data']


def obter_leituras(dados, id_hidrometro):
    leituras = []
    for leitura in dados['leituras']:
        if leitura['id_hidrometro'] == id_hidrometro:
            leituras.append(leitura)
    leituras.sort(key=chave_data)
    return leituras


def calcular_intervalo(anterior, atual):
    consumo = atual['valor_m3'] - anterior['valor_m3']
    data_anterior = date.fromisoformat(anterior['data'])
    data_atual = date.fromisoformat(atual['data'])
    dias = (data_atual - data_anterior).days
    return consumo, dias, consumo / dias


# Confere a leitura com os registros anteriores e posteriores do mesmo hidrômetro.
def validar_leitura(leituras, data_leitura, valor):
    for leitura in leituras:
        if leitura['data'] == data_leitura:
            return 'Registro recusado: já existe uma leitura nesta data.'
        elif leitura['data'] < data_leitura and leitura['valor_m3'] > valor:
            return 'Registro recusado: o valor não pode ser menor que uma leitura anterior.'
        elif leitura['data'] > data_leitura and leitura['valor_m3'] < valor:
            return 'Registro recusado: o valor não pode ser maior que uma leitura posterior.'
    return ''


# Registro de uma nova leitura
def registrar_leitura(dados):
    medidor = escolher(dados['hidrometros'])
    if medidor is None:
        return
    leituras = obter_leituras(dados, medidor['id'])
    if leituras:
        print(f"Última leitura: {leituras[-1]['data']} | {leituras[-1]['valor_m3']:.3f} m³")
    print('Você pode inserir datas anteriores. Use o valor acumulado que o hidrômetro mostrava naquela data.')
    data_leitura = ler_data()
    valor = ler_numero('Leitura acumulada em m³ (ex.: 150,250): ')
    erro = validar_leitura(leituras, data_leitura, valor)
    if erro:
        print(erro)
        return
    leitura = {'id': proximo_id(dados['leituras']), 'id_hidrometro': medidor['id'], 'data': data_leitura, 'valor_m3': valor}
    dados['leituras'].append(leitura)
    salvar_dados(dados)
    print('Leitura salva. Os intervalos foram atualizados pela ordem das datas.')
    print(gerar_relatorio(dados, medidor, '3'))


# Montagem do histórico, indicadores e alertas
def gerar_relatorio(dados, medidor, opcao):
    titulos = {'3': 'HISTÓRICO DE LEITURAS', '4': 'INDICADORES DO PERÍODO', '5': 'ALERTAS DE CONSUMO', '6': 'RELATÓRIO COMPLETO'}
    linhas = [titulos[opcao], '-' * 50]
    for residencia in dados['residencias']:
        if residencia['id'] == medidor['id_residencia']:
            linhas.append(f"Residência: {residencia['descricao']} | Comunidade: {residencia['comunidade']}")
    linhas.append(f"Hidrômetro: {medidor['identificacao']} | Limite atual: {medidor['limite_diario_m3']:.3f} m³/dia")
    leituras = obter_leituras(dados, medidor['id'])
    total = 0
    total_dias = 0
    alertas = 0
    for indice in range(len(leituras)):
        leitura = leituras[indice]
        if indice == 0:
            if opcao in ('3', '6'):
                linhas.append(f"{leitura['data']} | {leitura['valor_m3']:.3f} m³ | Leitura inicial")
        else:
            consumo, dias, media = calcular_intervalo(leituras[indice - 1], leitura)
            total += consumo
            total_dias += dias
            limite = medidor['limite_diario_m3']
            # Desconsidera resíduos da representação binária dos decimais.
            tolerancia = max(1e-9 * abs(media), 1e-9 * abs(limite), 1e-12)
            elevado = media > limite and abs(media - limite) > tolerancia
            situacao = 'Dentro do limite'
            if elevado:
                alertas += 1
                situacao = 'Acima do limite'
            if opcao == '5' and elevado:
                linhas.append(f"De {leituras[indice - 1]['data']} a {leitura['data']} | Média: {media:.3f} m³/dia | {situacao}")
            if opcao in ('3', '6'):
                linhas.append(f"{leitura['data']} | {leitura['valor_m3']:.3f} m³ | Consumo: {consumo:.3f} m³ em {dias} dias | Média: {media:.3f} m³/dia | {situacao}")
    if len(leituras) == 0:
        linhas.append('Nenhuma leitura registrada.')
    elif len(leituras) == 1:
        linhas.append('Dados insuficientes: são necessárias duas leituras para calcular consumo.')
    elif opcao in ('4', '6'):
        linhas.append(f"Período: {leituras[0]['data']} a {leituras[-1]['data']}")
        linhas.append(f'Leituras: {len(leituras)} | Intervalos: {len(leituras) - 1}')
        linhas.append(f'Consumo total: {total:.3f} m³ em {total_dias} dias')
        linhas.append(f'Média diária geral: {total / total_dias:.3f} m³/dia')
        linhas.append(f'Intervalos acima do limite: {alertas}')
    if opcao == '5' and len(leituras) >= 2 and alertas == 0:
        linhas.append('Nenhum intervalo acima do limite configurado.')
    if opcao in ('5', '6'):
        linhas.append('O alerta não comprova vazamento. O limite é uma regra configurável do protótipo.')
    return '\n'.join(linhas)


# Exibição e exportação das consultas
def excluir_leitura(dados):
    medidor = escolher(dados['hidrometros'])
    if medidor is None:
        return
    leituras = obter_leituras(dados, medidor['id'])
    if not leituras:
        print('Nenhuma leitura registrada para excluir.')
        return
    for leitura in leituras:
        print(f"ID {leitura['id']} | {leitura['data']} | {leitura['valor_m3']:.3f} m³")
    while True:
        escolha = input('ID da leitura a excluir (0 para voltar): ').strip()
        if escolha == '0':
            return
        selecionada = None
        for leitura in leituras:
            if escolha == str(leitura['id']):
                selecionada = leitura
        if selecionada is None:
            print('ID inexistente neste hidrômetro.')
            continue
        print(f"Excluir leitura de {selecionada['data']}, com {selecionada['valor_m3']:.3f} m³?")
        confirmacao = input('Digite s para confirmar ou outra tecla para cancelar: ').strip().lower()
        if confirmacao != 's':
            print('Exclusão cancelada.')
            return
        dados['leituras'].remove(selecionada)
        salvar_dados(dados)
        print('Leitura excluída. As consultas serão recalculadas com as leituras restantes.')
        return


def consultar_dados(dados, opcao):
    # As consultas usam os mesmos cálculos, mudando apenas o conteúdo exibido.
    medidor = escolher(dados['hidrometros'])
    if medidor is None:
        return
    texto = gerar_relatorio(dados, medidor, opcao)
    print('\n' + texto)
    if opcao == '6':
        resposta = input('Salvar cópia TXT? (s/n): ').strip().lower()
        if resposta == 's':
            caminho = os.path.join(PASTA, f"relatorio_{medidor['id']}.txt")
            with open(caminho, 'w', encoding='utf-8') as arquivo:
                arquivo.write(texto)
            print(f'Relatório salvo em {caminho}')


# Remove o cadastro e seus vínculos somente após a confirmação.
def excluir_cadastro(dados, tipo):
    cadastro = escolher(dados[tipo])
    if cadastro is None:
        return
    medidores_excluidos = []
    if tipo == 'residencias':
        print(f"Residência selecionada: {cadastro['descricao']}")
        for medidor in dados['hidrometros']:
            if medidor['id_residencia'] == cadastro['id']:
                medidores_excluidos.append(medidor['id'])
    else:
        print(f"Hidrômetro selecionado: {cadastro['identificacao']}")
        medidores_excluidos.append(cadastro['id'])
    quantidade_leituras = 0
    for leitura in dados['leituras']:
        if leitura['id_hidrometro'] in medidores_excluidos:
            quantidade_leituras += 1
    print(f'Serão excluídos {len(medidores_excluidos)} hidrômetro(s) e {quantidade_leituras} leitura(s).')
    if tipo == 'residencias':
        print('A residência também será excluída.')
    else:
        print('A residência continuará cadastrada.')
    confirmacao = input('Exclusão permanente. Digite s para confirmar ou outra tecla para cancelar: ').strip().lower()
    if confirmacao != 's':
        print('Exclusão cancelada.')
        return
    # Monta novas listas para não remover itens enquanto percorre a lista original.
    leituras_restantes = []
    for leitura in dados['leituras']:
        if leitura['id_hidrometro'] not in medidores_excluidos:
            leituras_restantes.append(leitura)
    medidores_restantes = []
    for medidor in dados['hidrometros']:
        if medidor['id'] not in medidores_excluidos:
            medidores_restantes.append(medidor)
    dados['leituras'] = leituras_restantes
    dados['hidrometros'] = medidores_restantes
    if tipo == 'residencias':
        dados['residencias'].remove(cadastro)
    salvar_dados(dados)
    print('Cadastro e registros vinculados excluídos.')
