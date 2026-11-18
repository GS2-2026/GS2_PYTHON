"""Programa principal: início, menu e chamada dos subalgoritmos."""
# Importa as funções que fazem as operações do sistema.
import subalgoritmos

OPCOES = ('1', '2', '3', '4', '5', '6', '7', '0')


def main():
    try:
        dados = subalgoritmos.carregar_dados()
    except (OSError, ValueError, TypeError):
        print('Não foi possível carregar os dados. O arquivo foi preservado. Confira dados/agua.json antes de tentar novamente.')
        return
    while True:
        print("""
ECOCOMUNIDADE - ÁGUA
1 - Cadastros
2 - Registrar leitura
3 - Histórico
4 - Indicadores
5 - Alertas
6 - Relatório e exportação
7 - Excluir leitura
0 - Sair
""")
        opcao = input('Opção: ').strip()
        if opcao not in OPCOES:
            print('Opção inválida.')
            continue
        try:
            match opcao:
                case '1':
                    subalgoritmos.menu_cadastros(dados)
                case '2':
                    subalgoritmos.registrar_leitura(dados)
                case '3' | '4' | '5' | '6':
                    subalgoritmos.consultar_dados(dados, opcao)
                case '7':
                    subalgoritmos.excluir_leitura(dados)
                case '0':
                    print('Até logo!')
                    return
        except OSError:
            print('Falha ao gravar arquivo. Confira permissões e espaço em disco. O programa será encerrado; alterações não salvas não serão mantidas.')
            return


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nPrograma encerrado.')
