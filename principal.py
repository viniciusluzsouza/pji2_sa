from threading import Thread, Event, Lock
from time import sleep
import json
from gerenciador import *
from mensagens_auditor import MsgSAtoSS
from copy import deepcopy
import random
import compartilhados
from status import *

class Principal:

    def __init__(self):
        gerente = Gerenciador()
        gerente.init_thread_rede()
        self.nome_r1 = ''
        self.nome_r2 = ''
        self.status = Status()

    def cadastrarRobo(self):

        # Cadastra robo
        #1
        self.nome_r1 = input("Nome: ")
        cor = int(input("Cor (int):"))
        mac = input("MAC: ")
        gerente.cadastra_robo(self.nome_r1, cor, mac)
        msg = {"_dir": "teste", "robo": self.nome_r1}
        msg.update({"cmd": MsgSAtoSS.CadastraRobo, "nome": self.nome_r1, "cor": cor, "mac": mac, "robo": "cadastro"})

        #2
        self.nome_r2 = input("Nome: ")
        cor = int(input("Cor (int):"))
        mac = input("MAC: ")
        gerente.cadastra_robo(self.nome_r2, cor, mac)
        msg = {"_dir": "teste", "robo": self.nome_r2}
        msg.update({"cmd": MsgSAtoSS.CadastraRobo, "nome": self.nome_r2, "cor": cor, "mac": mac, "robo": "cadastro"})

    def solicitarID(self, robo):
        # Solicita ID
        msg.update({"cmd": MsgSAtoSS.SolicitaID, "robo": robo})

    def getHistorico(self, robo):
        # Solicita historico
        msg.update({"cmd": MsgSAtoSS.SolicitaHistorico, "robo":robo})

    def NovoJogo(self):
        modo = int(input("Digite 1 para manual e 2 para automatico: "))
        x1, y1 = int(input("Defina as Coordenadas do robo", self.nome_r1,"\n ## 66 = (6, 6)"))
        x2, y2 = int(input("Defina as Coordenadas do robo", self.nome_r2,"\n ## 00 = (0, 0)"))

        self.status.definirPartida(self.nome_r1, x1, y1,
                                   self.nome_r2, x2, y2)


        print("Sorteando posição das caças...")
        cacas = []
        if int(modo) == 2:
            # Sorteia cacas
            for i in range(0, 5):
                caca = {}
                caca["x"] = random.randint(1, 5)
                caca["y"] = random.randint(1, 5)
                cacas.append(caca)

            print("Cacas: %s" % str(cacas))


        # Envia mensagem para o SS do Robo_1 e SS do Robo_2
        msg = ({"cmd": MsgSAtoSS.NovoJogo, "modo_jogo": modo, "cacas": cacas})

        with compartilhados.gerente_msg_lock:
            compartilhados.gerente_msg = deepcopy(msg)
            compartilhados.solicita_gerente.set()

        while True:
            print("""
             ### Escolha a opcao:
            1) Solicita Status
            2) Novo Jogo
            3) Pausa
            4) Continua
            5) Fim Jogo
            6) Atualiza Mapa
            0) EXIT
                    """)

            op = input("Opcao: ")

            if op == 1:
                # Solicita historico
                msg.update({"cmd": MsgSAtoSS.SolicitaStatus})



            elif op == 6:
                # Pausa
                msg.update({"cmd": MsgSAtoSS.Pausa})

            elif op == 7:
                # Continua
                msg.update({"cmd": MsgSAtoSS.Continua})

            elif op == 8:
                # Fim Jogo
                msg.update({"cmd": MsgSAtoSS.FimJogo})

            elif op == 9:
                print("Apenas uma caca ...")
                x = int(input("Caca (X): "))
                y = int(input("Caca (Y): "))
                adv_x = random.randint(0, 6)
                adv_y = random.randint(0, 6)
                print("Posicao Fake adversario: (%d,%d)" % (adv_x, adv_y))
                cacas = [{"x": x, "y": y}]
                adv = {"x": adv_x, "y": adv_y}
                msg.update({"cmd": MsgSAtoSS.AtualizaMapa, "cacas": cacas, "posicao_adversario": adv})

            elif op == 0:
                msg = {"cmd": -1, "_dir": "local"}


        print("*** Antes de mais nada, cadastre o robo !!! ***")
	print("Este nome sera usado para as mensagens enviadas ao robo")


	while True:

		except:
			print("Opcao invalida")
			continue

		with compartilhados.gerente_msg_lock:
			compartilhados.gerente_msg = deepcopy(msg)
			compartilhados.solicita_gerente.set()

		sleep(2)

		if op == 0: break