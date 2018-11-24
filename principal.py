from gerenciador import *
from status import *
import compartilhados
from copy import deepcopy
from mensagens_auditor import *

status = Status()
l = []
r = input("Cadastrar robo teste:")
status.definirPartida(r, 0, 0, 'roboB', 6, 6, l)

gerenciador = Gerenciador(status)
gerenciador.init_thread_rede()


## Interface de testes

while True:

    compartilhados.transmitir_toUI_event.wait()

    with compartilhados.transmitir_toUI_lock:
        msg = deepcopy(compartilhados.transmitir_toUI)
        print("interface", msg)
        if msg['cmd'] == MsgAuditorToUI.AtualizarR1:
            x, y = status.getCoordRobo(status.getRoboA())
            print(status.getRoboA(), "x:", x, "y:", y)

    compartilhados.transmitir_toUI_event.clear()