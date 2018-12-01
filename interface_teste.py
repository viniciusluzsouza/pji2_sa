import compartilhados
from copy import deepcopy
from mensagens_auditor import *
import random
from threading import Thread

class Inter(Thread):

    def __init__(self, status):
        Thread.__init__(self)
        self.status = status


    def avisar_gerenciador(self, msg):
        with compartilhados.gerente_msg_lock:
            compartilhados.gerente_msg = msg
            compartilhados.solicita_gerente.set()

    def run(self):

        print("========CONFIGURAÇÕES INICIAIS ===========")

        roboA = input("Nome do robo 1: ")
        x1 = input("Defina x inicial: ")
        y1 = input("Defina y inicial: ")
        roboB = input("Nome do robo 2: ")
        x2 = input("Defina x inicial: ")
        y2 = input("Defina y inicial: ")

        cacas = []

        # Sorteia cacas
        for i in range(0, 5):
            caca = {}
            caca["x"] = random.randint(1, 5)
            caca["y"] = random.randint(1, 5)
            cacas.append(caca)

        print("Cacas: %s" % str(cacas))

        # Define jogadores e caças
        self.status.definirPartida(roboA, x1, y1, roboB, x2, y2, cacas)

        # Seleciona o modo de Jogo
        modo = int(input("Definir modo de jogo\n (1) Autonomo \n (2) Manual\n"))
        msg = {}
        if modo == 1:
            msg = {'_dir': 'ui', '_robo': '', "cmd": MsgUItoAuditor.NovoJogo, "modo_jogo": 'autonomo', "cacas": cacas,
                   'jogadorA': roboA, 'xA': x1, 'yA': y1, 'jogadorB': roboB, 'xB': x2, 'yB': y2}

        elif modo == 2:
            msg = {'_dir': 'ui', '_robo': '', "cmd": MsgUItoAuditor.NovoJogo, "modo_jogo": 'manual', "cacas": cacas,
                   'jogadorA': roboA, 'xA': x1, 'yA': y1, 'jogadorB': roboB, 'xB': x2, 'yB': y2}

        print(msg)
        # Envia para todos o modo de jogo
        self.avisar_gerenciador(msg)



        ## Interface de testes

        while True:

            compartilhados.transmitir_toUI_event.wait()

            with compartilhados.transmitir_toUI_lock:
                msg = deepcopy(compartilhados.transmitir_toUI)

                if msg['cmd'] == MsgAuditorToUI.AtualizarRobo:
                    self.status.atualizarPosicaoRobo(msg['_robo'], msg['x'], msg['y'])

                if msg['cmd'] == MsgAuditorToUI.ValidarCaca:
                    print("ROBO: " + msg['_robo'] + " solicita validação de caça")
                    print("Na posição: ", '(', msg['x'], ',', msg['y'], ')')
                    x = 0
                    y = 0
                    if msg['_robo'] == self.status.getRoboA():
                        x, y = self.status.getCoordRobo(self.status.getRoboA())

                    elif msg['_robo'] == self.status.getRoboB():
                        x, y = self.status.getCoordRobo(self.status.getRoboB())
                    print("POSICAO DO ROBO: ", "(", x, ",", y, ")")


                    while True:
                        v = input("VALIDAR?\n(s) SIM\n(n) NÃO\n")
                        if v == 's':
                            msg = {'_robo': msg['_robo'], '_dir': 'ui', 'cmd': MsgUItoAuditor.ValidarCaca, 'validacao': 1, 'x': msg['x'], 'y': msg['y']}
                            self.avisar_gerenciador(msg)
                            break

                        else:
                            print("Comando invalido")





            compartilhados.transmitir_toUI_event.clear()