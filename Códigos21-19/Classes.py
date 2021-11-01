import numpy as np
import copy
from datetime import datetime
from interface_generated import Ui_MainWindow

ui = Ui_MainWindow()

# Data armazena os dados atuais
class Data:
    def __init__(self): #!Localizado em Data
        # Constantes
        self.wheelPosMax = 0
        self.wheelPosMin = 0
        self.pSizes = [20, 36, 34, 46] #todo: Deve ser conferido aquelas coisas do acionamento do spark e tals

        # Dados
        #?vou tentar utilizar aquilo de colocar isso tudo em packnames
        #self.p1Order = ['acelX_DD', 'acelY_DD', 'acelZ_DD', 'velAng',
        #                'velDE', 'velDD', 'velTE', 'velTD', 'rpm', 'beacon', 'hodometro', 'time']

        #self.p2Order = ['ext1', 'ext2', 'ext3', 'ext4', 'ext5', 'ext6', 'ext7', 'ext8', 'ext9', 'ext10', 'time2']

        #self.p3Order = ['tps', 'oleoP', 'fuelP', 'injectors', 'suspDE', 'suspDD', 'suspTE', 'suspTD',
        #                'volPos', 'correnteBat', 'correnteVent', 'correnteBomba', 'frontBrakeP',  'rearBrakeP', 'time3']

        #self.p4Order = ['batVoltage', 'ect', 'oilTemp', 'tempDiscoDE', 'tempDiscoDD', 'tempDiscoTE', 'tempDiscoTD',
        #                'tempVent', 'tempBomba', 'runners', 'releVent', 'releBomba', 'mata', 'gpsLat', 'gpsLong',
        #                'gpsNS', 'gpsEW', 'sparkCut', 'tempBat', 'time4'] #todo: Verificar se tem outro PosRunners
        
        self.updateDataFunctions = {1: self.updateP1Data, 2: self.updateP2Data, 3: self.updateP3Data, 4: self.updateP4Data}

        self.dic = {
            'acelX_DD': 0, 'acelY_DD': 0, 'acelZ_DD': 0, 'velAng': 0,
            'velDD': 0, 'velDE': 0, 'velTD': 0, 'velTE': 0, 'rpm': 0, 'beacon': 0, 'time': 0, 'hodometro': 0,

            'ext1': 0, 'ext2': 0, 'ext3': 0, 'ext4': 0, 'ext5': 0, 'ext6': 0, 'ext7': 0, 'ext8': 0, 'ext9': 0, 'ext10': 0, 'time2': 0,

            'tps': 0, 'oleoP': 0, 'fuelP': 0, 'injectors': 0, 'suspDE': 0, 'suspDD': 0, 'suspTE': 0, 'suspTD': 0,
            'volPos': 0, 'correnteBat': 0, 'correnteVent': 0, 'correnteBomba': 0, 'frontBrakeP': 0,  'rearBrakeP': 0, 'time3': 0,

            'batVoltage': 0, 'ect': 0, 'oilTemp': 0, 'tempDiscoDE': 0, 'tempDiscoDD': 0, 'tempDiscoTE': 0, 'tempDiscoTD': 0,
            'tempVent': 0, 'tempBomba': 0, 'runners': 0, 'releVent': 0, 'releBomba': 0, 'mata': 0, 'gpsLat': 0, 'gpsLong': 0,
            'gpsNS': 0, 'gpsEW': 0, 'gpsHora': 0, 'gpsData':0, 'sparkCut': 0, 'tempBat': 0, 'time4': 0 #!talvez ocorra erro por ter essa virgula
        }

        #?Estou fazendo teste com isso. pode dar certo ou nao
        #Lista com as chaves do dicionarios dic, isso é, o nome dos dados dos 4 pacotes
        self.packNames= list(self.dic.keys()) 

        self.dicRaw = copy.deepcopy(self.dic)
        self.alarms = copy.deepcopy(self.dic)
        # Configura alarmes padrao
        self.setDefaultAlarms()
        #Vetores para plotagem de gráficos na aba "Engine | Battery | Relay | GG" da interface
        #!Localizados em update
        self.arrayTemp = np.zeros(50)
        self.arrayFuelP = np.zeros(50)
        self.arrayOilP = np.zeros(50)
        self.arrayBattery = np.zeros(50)
        self.arrayTime2 = np.zeros(50) #? talvez eu tenha que atualizar isso aqui pros tempos atualizados
        self.arrayTime3 = np.zeros(50)


    def setDefaultAlarms(self): #!localizado em Alarms
        #apaga todos alarmes configurados até então na interface
        for key in self.alarms:
            self.alarms[key] = []

        #reseta os alarmes padrões com valores pré-configurados 
        #?atualizei com os alarmes padroes novos e alarmes de critico. PODE CAUSAR BUGS
        self.alarms['batVoltage'] = [12.0, 14.0, 'lesser than'] 
        self.alarms['ect'] = [80.0, 90.0, 'greater than']
        self.alarms['tempDiscoDE']=['',100.0, 'greater than']
        self.alarms['tempDiscoDD']=['',100.0, 'greater than']
        self.alarms['tempDiscoTE']=['',100.0, 'greater than']
        self.alarms['tempDiscoTD']=['',100.0, 'greater than']
        self.alarms['oilTemp']=['',3.0, 'equal to']
        self.alarms['oleoP']=['',1.0, 'greater than']
        #self.displayAlarm() #todo: conferir se isso é util e se causará algum bug


    # Caso valor seja signed, é necessario trata-lo como complemento de 2
    # Usado para os dados de aceleração
    def twosComplement(self, number, bits): #!localizado em Data
        if (number & (1 << (bits - 1))) != 0:
            number = number - (1 << bits)        # compute negative value
        return number

    #!localizados em Data
    #* Processamento e armazenamento do Pacote 1 
    def updateP1Data(self, buffer):
        if ((int(buffer[0]) == 1) and (len(buffer) == self.pSizes[0])):  # Testa se é o pacote 1 e se está completo.
            p1 = (self.packNames[0:11])
            # Acelerometros
            for i in range(0, 3):
                j = 2 + 2*i
                key = p1[i]
                self.dicRaw[key] = (buffer[j] << 8) + buffer[j+1] 
                self.dicRaw[key] = self.twosComplement(self.dicRaw[key], 16) # Complemento de 2
                self.dic[key] = round(float(self.dicRaw[key] / 16384), 3) 
            
            # Velocidade angular, 4 rodas, Rpm, beacon e tempo do pacote 
            self.dicRaw['velAng'] = int(buffer[8])
            self.dicRaw['velDD'] = int(buffer[9])
            self.dicRaw['velDE'] = int(buffer[10])
            self.dicRaw['velTD'] = int(buffer[11])
            self.dicRaw['velTE'] = int(buffer[12])
            self.dicRaw['rpm'] = (int(buffer[13]) << 8) + int(buffer[14])
            self.dicRaw['beacon'] = int(buffer[15])
            self.dicRaw['time'] = ((buffer[16]) << 8) + int(buffer[17])
            
            # Dados que não precisam de processamento
            self.dic['velAng'] = self.dicRaw['velAng'] #todo: verificar se necessita processamento
            self.dic['velDE'] = self.dicRaw['velDE']
            self.dic['velDD'] = self.dicRaw['velDD']
            self.dic['velTE'] = self.dicRaw['velTE']
            self.dic['velTD'] = self.dicRaw['velTD']
            self.dic['rpm'] = self.dicRaw['rpm']
            self.dic['beacon'] = self.dicRaw['beacon']

            # Beacon e Hodometro
            if(self.dic['beacon'] != 0):
                self.dic['hodometro'] += self.pistas[ui.trackOdometerComboBox.currentText()] #todo: conferir o nome desta classe, já que nao existe ui

            self.dic['time'] = 25 * self.dicRaw['time']
            return 1    
        else:
            return 0


    #* Processamento e armazenamento do Pacote 2
    #* Somente dados de extensometria, tratamentos mais simples, por ser um unica tipo de dado
    def updateP2Data(self, buffer):
        if ((int(buffer[0]) == 2) and (len(buffer) == self.pSizes[1])):  # testa se é o pacote 2 e se está completo
            p2 = (self.packNames[12:22]) 
            for i in range(0, len(p2) -1): #len(p2)-1 por causa do 'time'
                j = 2 + 3*i
                key = p2[i]
                self.dicRaw[key] = (buffer[j] << 16) + (buffer[j+1] << 8) + buffer[j+2]
                self.dic[key] = self.dicRaw[key]
            self.dicRaw['time2'] = (buffer[32] << 8) + (buffer[33])
            self.dic['time2'] = 25 * self.dicRaw['time2']
            return 1
        else:
            return 0


    #* Processamento e armazenamento do Pacote 3
    def updateP3Data(self, buffer):
        if ((int(buffer[0]) == 3) and (len(buffer) == self.pSizes[2])):  #Testa se é o pacote 3 e se está completo
            p3 = (self.packNames[23:37]) 
            #.Todos os dados do pacote 3 sao no formato byte1 << 8 | byte2 
            # Se realiza soma dos 2 bytes para cada dado e armazena em dicRaw
            for i in range(0, len(p3)):
                j = 2 + 2*i   
                key = p3[i]
                self.dicRaw[key] =  (buffer[j] << 8) + buffer[j+1]

            # Processamento dos dados
            self.dic['tps'] = 0.1*self.dicRaw['tps']
            self.dic['oleoP'] = round(float(self.dicRaw['oleoP'] * 0.001), 4)
            self.dic['fuelP'] = round(float(self.dicRaw['fuelP'] * 0.001), 4)
            self.dic['rearBrakeP'] = round(self.dicRaw['rearBrakeP'] * 0.02536, 2)
            self.dic['frontBrakeP'] = round(self.dicRaw['frontBrakeP'] * 0.02536, 2)
            
            #Valores de wheelPosMax e wheelPosMin são constantes definidas pelo usuário na interface
            if self.wheelPosMax - self.wheelPosMin != 0:
                self.dic['volPos'] = round(((self.dicRaw['volPos'] - self.wheelPosMin) * 240 / (self.wheelPosMax - self.wheelPosMin) - 120), 2)
            
            self.dic['injectors'] = self.dicRaw['injectors']
            self.dic['correnteBat'] = round(self.dicRaw['correnteBat'] * 0.014652, 3) - 29.3
            self.dic['suspDE'] = self.dicRaw['suspDE']
            self.dic['suspDD'] = self.dicRaw['suspDD']
            self.dic['suspTE'] = self.dicRaw['suspTE']
            self.dic['suspTD'] = self.dicRaw['suspTD']
            self.dic['correnteVent'] = self.dicRaw['correnteVent']
            self.dic['correnteBomba'] = self.dicRaw['correnteBomba']
            self.dic['time3'] = 25 * self.dicRaw['time3']
            return 1
        else:
            return 0


    #* Processamento e armazenamento do Pacote 4
    def updateP4Data(self, buffer):
        if ((int(buffer[0]) == 4) and (len(buffer) == self.pSizes[3])):  #Testa se é o pacote 4 e está completo
            p4 = (self.packNames[38:59])
            # os 10 primeiros dados sao no formato byte1 <<8 | byte2 
            for i in range(0, 10):
                j = 2 + 2*i
                key = p4[i]                
                self.dicRaw[key] = (buffer[j] << 8) + buffer[j+1]
            
            # Dados que ocupam mais de 2 bytes, sendo somados e atribuidos em dicRaw
            self.dicRaw['releBomba'] = int((buffer[22] & 128) >> 7) 
            self.dicRaw['releVent'] = int((buffer[22] & 8) >> 3)    
            self.dicRaw['mata'] = int((buffer[22] & 32) >> 5)
            self.dicRaw['gpsLat'] = (buffer[23] << 16) + (buffer[24] << 8) + buffer[25]
            self.dicRaw['gpsLong'] = (buffer[26] << 16) + (buffer[27] << 8) + buffer[28]
            self.dicRaw['gpsNS'] = int(buffer[29])
            self.dicRaw['gpsEW'] = int(buffer[30])
            '''Falta gps hora, minuto, segundo, ms, ano, mes dia nessa ordem (posicoes 31 - 37)'''
            self.dicRaw['time4'] = (buffer[38] << 8) + buffer[39]
            self.dicRaw['sparkCut'] = (buffer[40] << 8) + buffer[41]
            self.dicRaw['tempBat'] = (buffer[42] << 8) + buffer[43]

            #Processamento dos dados
            self.dic['batVoltage'] = round(float(self.dicRaw['batVoltage'] * 0.01), 2)
            self.dic['ect'] = round(float(self.dicRaw['ect'] * 0.1), 2)
            self.dic['oilTemp'] = self.dicRaw['oilTemp']
            self.dic['tempDiscoDE'] = round(float(self.dicRaw['tempDiscoDE']), 2)
            self.dic['tempDiscoDD'] = round(float(self.dicRaw['tempDiscoDD']), 2)
            self.dic['tempDiscoTE'] = round(float(self.dicRaw['tempDiscoTE']), 2)
            self.dic['tempDiscoTD'] = round(float(self.dicRaw['tempDiscoTD']), 2)
            self.dic['tempVent'] = self.dicRaw['tempVent']
            self.dic['tempBomba'] = self.dicRaw['tempBomba']
            self.dic['runners'] = self.dicRaw['runners']
            self.dic['releVent'] = 'ON' if self.dicRaw['releVent'] == 1 else 'OFF'
            self.dic['releBomba'] = 'ON' if self.dicRaw['releBomba'] == 1 else 'OFF'
            self.dic['mata'] = 'ON' if self.dicRaw['mata'] == 1 else 'OFF'
            self.dic['gpsLat'] = self.dicRaw['gpsLat']
            self.dic['gpsLong'] = self.dicRaw['gpsLong']
            self.dic['gpsNS'] = self.dicRaw['gpsNS']
            self.dic['gpsEW'] = self.dicRaw['gpsEW']
            self.dic['time4'] = 25 * self.dicRaw['time4']
            return 1
        
        else:
            return 0


    def rollArrays(self): #*localizado em Update
        #funcao para manter o vetor ordenado da mensagem mais antiga a mais nova
        #atualizando o ultimo valor e "empurrando" em uma posicao
        self.arrayBattery = np.roll(self.arrayBattery, -1)
        self.arrayBattery[-1] = self.dic['batVoltage']
        self.arrayOilP = np.roll(self.arrayOilP, -1)
        self.arrayOilP[-1] = self.dic['oleoP']
        self.arrayTemp = np.roll(self.arrayTemp, -1)
        self.arrayTemp[-1] = self.dic['ect']
        self.arrayFuelP = np.roll(self.arrayFuelP, -1)
        self.arrayFuelP[-1] = self.dic['fuelP']
        self.arrayTime2 = np.roll(self.arrayTime2, -1)
        self.arrayTime2[-1] = self.dic['time2']
        self.arrayTime3 = np.roll(self.arrayTime3, -1)
        self.arrayTime3[-1] = self.dic['time3']


    # Cria string unificada com dados do pacote packID, todos separados por espaço
    # Padroniza formato da string com dados obtidos para gravação em arquivo
    def createPackString(self, packNo): #!localizado em SaveFile
        #?Aqui usava aquilo do pack order. Atualizei com posicoes e tals
        #Fatia lista de valores com intervalo de dados referente ao pacote do identificador ID 
        #e insere ID do pacote na primeira posição da lista
        if packNo == 1:
            list=(self.data.packNames[0:11])
        elif packNo == 2:
            list=(self.data.packNames[12:22])
        elif packNo == 3:
            list=(self.data.packNames[23:37])
        elif packNo == 4:
            list=(self.data.packNames[38:59])

        delimiter = ' '
        vec = [packNo]
        for key in list:
            vec.append(self.dicRaw[key])
        string = delimiter.join(str(x) for x in vec)
        string = string + '\n'
        return string


# Classe armazena um arquivo
class File:
    def __init__(self):
        self.save = 0


    def startDataSave(self, arquivo): #!localizado em SaveFile como startSave
        now = datetime.now()

        #todo: testar esse trecho aqui, ver q q ele faz e se da bom
        #Nome do arquivo selecionado pelo usuário
        #arquivo = ui.lineEdit_FileName.text()

        # define o nome do arquivo concatenando o nome definido pelo usuário e hora e minuto do início da gravação
        arquivo = arquivo + "_" + str(now.hour) + "_" + str(now.minute) + ".txt"
        print(arquivo)
        self.arq = open(arquivo, 'w')

        #todo:checar se da merda se eu incluir esse novo trecho
        #self.headerFile() # escreve as informações de cabelho no inicio do arquivo
        self.save = 1
        #todo:checar esse trem do ui
        #ui.label_12.setText("Saving...")  # informa ao usuário a situação atual de gravação de dados

    # Escreve dados de Setup no início do arquivo e dados recebidos de um pacote
    def writeRow(self, string): #!localizado em SaveFile
        self.arq.write(string)


    # Função para parar a gravação dos dados no arquivo txt
    def stopDataSave(self): #!localizado em SaveFile como stopSave
        if self.save != 0: #verifica se tem algum arquivo texto aberto sendo gravado
            hodometro= ('Total final de metros rodados: ')+ str(Data.dic['hodometro']) #todo: ajustar essa self.data.dic
            self.writeRow(hodometro)
            self.save = 0  # atualiza o valor da variavel save, a qual é usada para verificar se está ocorrendo ou não não gravação dos dados
            self.arq.close()
            ui.label_12.setText("Saving stop...")  # informa ao usuário a situação atual de gravação de dados


# Escrve mensagens na instancia logInstance.
# Nesse caso, logInstance é um campo da interface. Pode ser qualquer campo que aceite a
# Funcao setText
class Log(): #!localizado em Log
    def __init__(self, logInstance, maxElements=200):
        self.Log = []
        self.logInstance = logInstance
        self.maxElements = maxElements
        self.on = 'on' #todo: no novo ele inicializa como off. Verificar isso


    # Insere novo texto de erro na primeira posicao do vetor
    def writeLog(self, text):
        if self.on == 'off':
            return

        self.Log.append(" ")
        # Faz o roll (Arrasta dados, apagando a informação mais antiga e subtituindo pela mais recente)
        if len(self.Log) < self.maxElements:
            self.Log = self.Log[-1:] + self.Log[:-1]
            self.Log[0] = text
        else:
            self.Log = self.Log[-1:] + self.Log[:self.maxElements-1]
            self.Log[0] = text
        string = '\n'.join(str(x) for x in self.Log)
        #string = string + '\n'
        self.logInstance.setText(string)
        # print(text)


# Concatena vetor em uma string separada por delimiter
def vectorToString(line, delimiter, addNewLine=True): #!localizado em Biblioteca
    string = delimiter.join(str(x) for x in line)
    if addNewLine:
        string = string + '\n'
    return string
