
import serial
from Classes import Data, File, Log, vectorToString
from PyQt5 import QtCore
import time


# Classe que executa o programa
class Program():
    def __init__(self, updateTime, errorLog, bufferLog, updateInterfaceFunctions, updateCounterMax=[0,0,0,0]):
        #*localizados na classe __init__ em Update
        self.updateTime = updateTime
        self.data = Data() 
        self.dataFile = File()
        # self.lapTimeFile = File()
        self.lastBuffers = bufferLog #Verifica condição de botão da interface
        self.errorLog = errorLog #Verifica condição de botão da interface
        #!aqui não tem self.alarms nem self.stop

        # Dicionario de funcoes: permite chamar funcoes fazendo updateInterfaceFunctions[key], onde key é 1,2,3 ou 4
        self.updateInterfaceFunctions = updateInterfaceFunctions

        self.packIndexes = [1, 2, 3, 4]
        self.packSizes = self.data.pSizes
        self.updateCounterMax = updateCounterMax  # numero de pacotes recebidos at atualizar a interface
        self.updateCounter = [0, 0, 0, 0] # numero de pacotes recebidos desde a ultima atualizacao da interface
        self.updateInterfaceEnabled = True # variavel que habilita ou desabilita a atualizacao da interface


    def openSerialPort(self, port, baudrate, timeout): #*localizado em SerialPort
        #configura parâmetros, como taxa de transmissão (baudrate), para a abertura da porta serial
        self.porta = serial.Serial()
        self.porta.baudrate = baudrate
        self.porta.port = port
        self.porta.timeout = timeout
        #abre porta selecionada
        self.porta.open()


    def stopProgram(self): #*localizado em Program
        self.stop = 1  # atualiza o valor da variavel stop, a qual é usada para verificar o funcionamento da interface
        # self.lapTimeFile.stopDataSave()
        # Fecha arquivo file e porta serial
        self.dataFile.stopDataSave()
        if self.porta.isOpen():
            self.porta.flushInput()
            self.porta.close()
        else:
            pass


    # program() roda em loop
    def program(self): #*localizado em Program
        if (self.stop == 0):
            # Le dados da porta serial
            self.buffer = self.readFromSerialPort(self.packSizes, self.packIndexes)

            if len(self.buffer) != 0:
                # chamada da função updateDataAndInterface para analisar os dados recebidos atualizar os mostradores da interface
                self.updateData(self.buffer, int(self.buffer[0]))
                if self.dataFile.save == 1:
                    self.saveLine(self.buffer, int(self.buffer[0]))
                if self.updateInterfaceEnabled:
                    self.updateInterface(self.buffer, int(self.buffer[0]))


            # Apos updateTime segundos, chama funcao program() novamente
            QtCore.QTimer.singleShot(self.updateTime, lambda: self.program())


    def updateData(self, buffer, packID): #*localizado em Update linha 58
        # Atualiza dados em Data e atualiza campos respectivos na interface
        if (self.data.updateDataFunctions[packID](buffer) == 0):
            self.errorLog.writeLog(" updateData: Pacote " + str(packID) + "com tamanho diferente do configurado") 
    #todo: atualizar essa parte com novos pacotes (nao tenho certeza)
        # Desloca vetores e chama funcao de atualizar graficos da interface
        if packID == 2 or packID == 3:
            self.data.rollArrays()


    def updateInterface(self, buffer, packID): #!localizado em Update
        # Chama funcao updatePxInterface, atribuida no dicionario updateInterfaceFunctions, para a chave x = packID
        if self.updateCounter[packID-1] >= self.updateCounterMax[packID-1]:
            self.updateInterfaceFunctions[packID](self.data)
            self.updateCounter[packID-1] = 0
        else:
            self.updateCounter[packID-1] += 1
        # Atualiza o mostrador textBrowser_Buffer com as ultimas listas de dados recebidas.
        self.lastBuffers.writeLog(vectorToString(buffer, ' ', addNewLine=False))


    def saveLine(self, buffer, packID): #!nao existe no programa novo
        # Grava linha buffer no arquivo
        string = self.data.createPackString(packID)
        self.dataFile.writeRow(string)


    # Le buffer da porta serial. bufferSize é uma lista com os tamanhos dos pacotes e firstByteValues
    # é uma lista com os numeros dos pacotes (1,2,3,4)
    def readFromSerialPort(self, bufferSize, firstByteValues): #*localizado em SerialPort
        #Leitura dos primeiro dois bytes do vetor, verificando se buffer recebido esta no formato correto
        while True:
            # Espera receber algo na porta serial
            while (self.porta.inWaiting() == 0):
                pass

            # Verifica se primeiro byte corresponde a um dos pacotes (1,2,3 ou 4)
            # Faz comparações implementadas, em que sempre o primeiro e segundo byte do pacote tem que ser o núm. do pacote e 5 respectivamente
            read_buffer = b'' 
            # Le primeiro e segundo bytes
            firstByte = self.porta.read()

            if int.from_bytes(firstByte, byteorder='big') in firstByteValues:
                read_buffer += firstByte
                # Le o segundo byte de inicio
                a = self.porta.read()
                if int.from_bytes(a, byteorder='big') == 5:
                    read_buffer += a
                    break
                else:
                    self.errorLog.writeLog("Leitura: segundo byte com valor inesperado. Leu-se " + str(firstByte) + ", esperava-se 5")
            # Se o byte lido nao for 1, 2 3 ou 4,, quer dizer que perdeu algum dado.
            else:
                self.errorLog.writeLog("Leitura: primeiro byte com valor inesperado. Leu-se " + str(firstByte) + ", esperava-se de 1 a 4")
        while True:
            # Le resto do buffer
            #index é o numero do pacote que o buffer esta enviando
            index = int.from_bytes(firstByte, byteorder='big') - 1
            #le quantos bytes tem no vetor, além dos dois já lidos anteriormente
            byte = self.porta.read(size=int(bufferSize[index] - 2))
            read_buffer += byte

            # Compara se o pacote tem o tamanho esperado
            # Faz comparações implementadas, em que sempre o penultimo e o último valor do pacote tem que ser 9 e 10 respectivamente
            if(len(read_buffer) == bufferSize[index]):
                if int(read_buffer[bufferSize[index]-2]) == 9:
                    # Chegou no fim do pacote
                    if int(read_buffer[bufferSize[index]-1]) == 10:
                        break
                    else:
                        self.errorLog.writeLog("Leitura: ultimo dado diferente de byte 10" + str(read_buffer))
                        return []
                else:
                    self.errorLog.writeLog("Leitura: penultimo dado diferente de byte 9")
                    return []
        
        # Retorna buffer de dados lidos do respectivo pacote
        return read_buffer
