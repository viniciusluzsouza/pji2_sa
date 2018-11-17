from threading import Thread, Lock, Event
from mensagens_auditor import *
from gerente_db import GerenteDB
from transmissor import *
from receptor import *
from copy import deepcopy
import compartilhados
from status import *


class Gerenciador():
    """Gerenciador do SA. Trata mensagens vindas de qualquer lugar."""

    def __init__(self, status):
        compartilhados.init()

        # Inicializa classe compartilhada com UI
        self.status = status

        # Inicializa o banco de dados
        self.gerente_db = GerenteDB()
        self.gerente_db.cria_db()

        # Inicializa transmissor
        self.transmissor = Transmissor("localhost")
        self.transmissor.start()

        # Inicializa receptor
        self.receptor = Receptor("localhost")
        self.receptor.start()

        super(Gerenciador, self).__init__()

    def get_cadastros(self):
        return self.gerente_db.get_cadastros()

    def cadastra_robo(self, nome, cor, mac):
        return self.gerente_db.cadastra_robo(nome, cor, mac)

    def salva_historico(self, robo_a, cacas_a, robo_b, cacas_b):
        self.gerente_db.salva_partida(robo_a, cacas_a, robo_b, cacas_b)

    def get_historico(self):
        return self.gerente_db.get_partidas()

    def _envia_msg_ss(self, msg):
        with compartilhados.transmitir_msg_lock:
            compartilhados.transmitir_msg = msg
            compartilhados.transmitir_event.set()

    def _envia_msg_ui(self, msg):
        with compartilhados.transmitir_toUI_lock:
            compartilhados.transmitir_toUI = msg
            compartilhados.transmitir_toUI.set()

    def init_thread_rede(self):
        def gerencia_msg_rede():
            while True:
                # Espera alguma mensagem ...
                compartilhados.solicita_gerente.wait()

                with compartilhados.gerente_msg_lock:
                    msg = deepcopy(compartilhados.gerente_msg)

                    if 'cmd' not in msg:
                        solicita_gerente.clear()
                        continue

                    cmd = msg['cmd']

                    if '_dir' in msg and msg['_dir'] == 'local' and cmd == -1:
                        break

                    # Solicitacoes vindas do SS
                    if '_dir' in msg and msg['_dir'] == 'ss':
                        print("Recebi msg do SS: ")
                        print("%s \n" % str(msg))

                        # Quando o Robo diz que está indo para tal lugar
                        # Implica-se que ele verificou a possibilidade dessa movimentacao
                        if cmd == MsgSStoSA.MovendoPara:
                            self.status.atualizarRobo(msg['_robo'], msg['x'], msg['y'])
                            # Avisa interface usuario
                            msg = {"cmd": MsgAuditorToUI.AtualizarR1, 'x': msg['x'], 'y': msg['y']}
                            self._envia_msg_ui(msg)

                        elif cmd == MsgSStoSA.PosicaoAtual:
                            # Caso a posição do robo não seja igual aquela que consta no status, avise UI
                            if not self.status.getCoordRobo(msg['_robo']) == msg['x'] and not self.status.getCoordRobo(
                                    msg['_robo']) == msg['y']:
                                self.status.atualizarPosicaoRobo(msg['_robo'], msg['x'], msg['y'])
                                msg = {"cmd": MsgAuditorToUI.AtualizarR1, "_robo": msg['_robo'], 'x': msg['x'],
                                       'y': msg['y']}
                                self._envia_msg_ui(msg)


                        elif cmd == MsgSStoSA.ValidaCaca:
                            # Teste: valida tudo
                            self.status.atualizarCacas(msg['_robo'], msg['x'], msg['y'])

                            # Ao validar a caça
                            if len(self.status.getCacas()) > 0:
                                # Jogo segue, avisa a ui
                                msg = {"cmd": MsgAuditorToUI.ValidarCaca, "_robo": msg['_robo'], 'x': msg['x'],
                                       'y': msg['y']}
                                self._envia_msg_ui(msg)
                            else:
                                # Teve um vencedor, avisa a ui
                                msg = {"cmd": MsgAuditorToUI.DeclararVencedor, "_robo": msg['_robo'], 'x': msg['x'],
                                       'y': msg['y']}
                                self._envia_msg_ui(msg)

                        elif cmd == MsgSStoSA.ObstaculoEncontrado:
                            msg = {"cmd": MsgAuditorToUI.Obstaculo, "_robo": msg['_robo']}
                            self._envia_msg_ui(msg)
                            # Avisa interface usuario
                            pass

                        elif cmd == MsgSStoSA.SolicitaID_Resp:
                            # Avisa interface usuario
                            pass

                        elif cmd == MsgSStoSA.SolicitaHistorico_RESP:
                            # Avisa interface usuario
                            pass

                        elif cmd == MsgSStoSA.SolicitaStatus_RESP:
                            # Avisa interface usuario
                            pass

                        else:
                            # Comando nao identificado, nao faz nada ...
                            pass

                    # Solicitacoes vindas da interface de usuario
                    elif '_dir' in msg and msg['_dir'] == 'ui':
                        '''
                        Sugestao: as classes interface usuario e principal
                        podem se comunicar com o gerente da mesma forma que
                        o SS se comunica com o SA (atraves de mensagens JSON).
                        Isto deve facilitar a implementacao, pois ja temos
                        o cenario montado, basta criar os IF's ...
    
                        if cmd == MsgUItoGerente.NovoJogo:
                            # Transmite para SS
    
                        elif ...
                        '''

                        if 'cmd' not in msg:
                            solicita_gerente.clear()
                            continue

                        cmd = msg['cmd']

                        if cmd == MsgUItoAuditor.FimdeJogo:
                            self.salva_historico(self.status.getRoboA(), self.status.getCacaRoboA(),
                                                 self.status.getRoboB(), self.status.getCacaRoboB())

                        elif cmd == MsgUItoAuditor.CadastrarRobo:
                            self.cadastra_robo(msg['_robo'], msg['cor'], msg['mac'])

                        elif cmd == MsgUItoAuditor.RecuperarCadastros:
                            self.status.setDBtoStatus(self.get_cadastros())
                            msg = {"cmd": MsgAuditorToUI.RecuperarCadastro}
                            self._envia_msg_ui(msg)

                        elif cmd == MsgUItoAuditor.RecuperarHistorico:
                            self.status.setDBtoStatus(self.get_historico())
                            msg = {"cmd": MsgAuditorToUI.RecuperarHistorico_RESP}
                            self._envia_msg_ui(msg)

                        elif cmd == MsgUItoAuditor.ValidarCaca:
                            msg = {"cmd": MsgSAtoSS.ValidacaoCaca, "_robo": msg['_robo']}
                            self._envia_msg_ss(msg)

                        else:
                            pass


                    # Solicitacoes vindas da classe principal
                    elif '_dir' in msg and msg['_dir'] == 'pr':
                        # Aqui podemos fazer da mesma forma ...
                        pass

                    elif '_dir' in msg and msg['_dir'] == 'teste':
                        # No teste, so envia para baixo ...
                        with compartilhados.transmitir_msg_lock:
                            compartilhados.transmitir_msg = msg
                            compartilhados.transmitir_event.set()

                    compartilhados.solicita_gerente.clear()

        t = Thread(target=gerencia_msg_rede)
        t.start()
        return


if __name__ == '__main__':
    print("Inicializando ...")
    status = Status()
    gerente = Gerenciador(status)
    gerente.init_thread_rede()
'''
### TESTE:
if __name__ == '__main__':
    print("Inicializando ...")
    gerente = Gerenciador()
    gerente.init_thread_rede()

    for i in range(1, 3):
        print("\nCadastrando %dº robo" % i)
        try:
            nome = input("Nome: ")
            cor = int(input("Cor (int): "))
            mac = input("MAC: ")
        except:
            print("Invalido")
            exit()

        gerente.cadastra_robo(nome, cor, mac)

    print("\nSalvando historico")
    try:
        roboA = input("Primeiro robo: ")
        roboB = input("Segundo robo: ")
        cacasA = int(input("Cacas encontradas primeiro robo (int): "))
        cacasB = int(input("Cacas encontradas segundo robo (int): "))
    except:
        print("Invalido")
        exit()

    gerente.salva_historico(roboA, cacasA, roboB, cacasB)

    print("\nExibindo cadastros ... ")
    cadastros = gerente.get_cadastros()
    for cadastro in cadastros:
        print(cadastro)

    print("\nExibindo historico ... ")
    partidas = gerente.get_historico()
    for partida in partidas:
        print(partida)

    import time
    time.sleep(2)
    print("\nMandando msg por thread ... ")

    with gerente_msg_lock:
        gerente_msg = {'cmd': MsgSStoSA.MovendoPara, '_dir': 'ss'}
        solicita_gerente.set()

    time.sleep(2)
    print("\nEnviando msg para finalizar!!")
    with gerente_msg_lock:
        gerente_msg = {'cmd': -1, '_dir': 'local'}
        solicita_gerente.set()

    print("FIM")
'''
