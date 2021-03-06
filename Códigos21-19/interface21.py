import PyQt5
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
# pacotes necessários
import sys
import glob
import numpy as np
import time

import serial
from Classes import Data, File, Log, vectorToString
from Program import Program
from interface_generated import Ui_MainWindow


# A função loadSetup atualiza os campos que já haviam sido definidos em utilizações ateriores da interface
# Ela serve para que não seja necessário atualizar todos os campos sempre que for necessária o reinício da interface
def loadSetup(): #!localizado em Setup
    # Primeira verificação e tratamento de exceção
    global settings, errorLog
    try:
        filename = settings.value('filename')
        ui.lineEdit_FileName.setText(filename)
    except:
        errorLog.writeLog("Erro ao carregar config do arquivo")

    # Segunda verificação e tratamento de exceção
    try:
        ui.textEdit_SetupComments.setText(settings.value('setupComments'))
        ui.lineEdit_WheelPosMax.setText(settings.value('wheelPosMax'))
        ui.lineEdit_WheelPosMin.setText(settings.value('wheelPosMin'))
        ui.lineEdit_CalibrationConstant.setText(settings.value('calibConstant'))
        ui.lineEdit_SetupCar.setText(settings.value('setupCar'))
        ui.lineEdit_SetupTrack.setText(settings.value('setupTrack'))
        ui.lineEdit_SetupDriver.setText(settings.value('setupDriver'))
        ui.lineEdit_SetupTemperature.setText(settings.value('setupTemp'))
        ui.lineEdit_SetupAntiroll.setText(settings.value('setupAntiroll'))
        ui.lineEdit_SetupTirePressureFront.setText(settings.value('tirePFront'))
        ui.lineEdit_SetupTirePressureRear.setText(settings.value('tirePRear'))
        ui.lineEdit_SetupWingAttackAngle.setText(settings.value('aeroAngle'))
        ui.lineEdit_SetupEngineMap.setText(settings.value('engineMap'))
        ui.lineEdit_SetupBalanceBar.setText(settings.value('balanceBar'))
        ui.lineEdit_SetupDifferential.setText(settings.value('setupDrexler'))
        ui.textEdit_SetupComments.setText(settings.value('setupComments'))
        ui.lineEdit_SampleRate1.setText(settings.value('sampleRate1'))
        ui.lineEdit_SampleRate2.setText(settings.value('sampleRate2'))
        ui.lineEdit_SampleRate3.setText(settings.value('sampleRate3'))
        ui.lineEdit_SampleRate4.setText(settings.value('sampleRate4'))
    except:
        errorLog.writeLog("Erro ao carregar configs")
    
    try:
        for key in program.data.alarms:
            if settings.contains('alarm'+key):
                store = settings.value('alarm'+key)
                store[0] = float(store[0])
                program.data.alarms[key] = store
    except:
        errorLog.writeLog("Erro ao carregar config de alarme")


# Atualiza portas seriais disponiveis
def updatePorts(): #!localizado em SerialPort
    ui.comboBox_SerialPorts.clear() #apaga lista atual
    ui.comboBox_SerialPorts.addItems(listSerialPorts()) #mostra lista atualizada de portas


def displayErrorMessage(text): #!localizado em Biblioteca
    dlg = QMessageBox(None)
    dlg.setWindowTitle("Error!")
    dlg.setIcon(QMessageBox.Warning)
    dlg.setText(
     "<center>" + text + "<center>")
    dlg.exec_()


# Lista as portas seriais disponiveis. Retorna uma lista com os nomes das portas
def listSerialPorts(): #!localizado em SerialPort
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    #Leitura de portas seriais disponiveis de acordo com sistema operacional utilizado
    #sistema operacional Windows
    if sys.platform.startswith('win'):
        ports = ['COM{}'.format(str(i + 1)) for i in range(256)]
    
    #sistema operacional Linux ou Unix
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    #sistema operacional Mac OS
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    #sistema não suportado pela interface, lança exceção da classe padrão EnvironmentError
    else:
        raise EnvironmentError('Unsupported platform')

    # Deixa todos portas seriais disponiveis fechadas para o programa, deixando o usuário selecionar qual deseja abrir
    # Cria vetor com lista de portas disponiveis a serem retornadas
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        #lança exceção, caso não seja possivel fechar uma porta serial, indicando que ela está 
        #sendo utilizada por outro programa do SO, não a incluindo na lista de disponiveis ao usuário
        except (OSError, serial.SerialException):
            pass

    #retorna vetor (result) com lista de portas seriais disponiveis ao usuario
    return result


# Função que inicia a execução do programa
def startProgram(): #!localizado em Program
    try:
        global errorLog, program
        # abre e configura a porta serial utilizando os valores definidos pelo usuário através da interface
        baudrate = int(ui.comboBox_Baudrate.currentText())
        port = str(ui.comboBox_SerialPorts.currentText())
        timeout = None
        program.openSerialPort(port, baudrate, timeout)

        # Inicializa programa e coloca constantes
        updateConstants()
        program.stop = 0
        # program.lapTimeFile.startDataSave("tempos_de_volta")
        program.updateTime = ui.doubleSpinBox_UpdateTime.value() * 1000
        if ui.lineEdit_SampleRate1.text() == "" or ui.lineEdit_SampleRate2.text() == "" or ui.lineEdit_SampleRate3.text() == "" or ui.lineEdit_SampleRate4.text() == "":
            displayErrorMessage("Inserir taxa de amostragem dos pacotes")
        else:
            program.program()


# O erro de porta serial é analisado pela exceção serial.SerialException. Esse erro é tratado pausando o programa e
# utilizando uma caixa de diálogo, a qual informa ao usuário o erro encontrado
    except serial.serialutil.SerialException:
        errorLog.writeLog("startProgram: SerialException")
        program.stopProgram()
        dlg = QMessageBox(None)
        dlg.setWindowTitle("Error!")
        dlg.setIcon(QMessageBox.Warning)
        dlg.setText(
         "<center>Failed to receive data!<center> \n\n <center>Check Serial Ports and Telemetry System.<center>")
        dlg.exec_()


# Atualiza constantes com os valores lidos na interface
def updateConstants(): #!localizado em Update
    global program
    if ui.lineEdit_WheelPosMax.text() != '' and ui.lineEdit_WheelPosMin.text() != '':
        program.data.wheelPosMax = int(ui.lineEdit_WheelPosMax.text())
        program.data.wheelPosMin = int(ui.lineEdit_WheelPosMin.text())
    program.updateCounterMax[0] = int(ui.updateCounterP1.value())
    program.updateCounterMax[1] = int(ui.updateCounterP2.value())
    program.updateCounterMax[2] = int(ui.updateCounterP3.value())
    program.updateCounterMax[3] = int(ui.updateCounterP4.value())


# Função para definir nome do arquivo txt no qual os dados serão gravados,
# abrir este arquivo e gravar dados de setup e os dados recebidos através na porta seria
def beginDataSave(): #!localizado em SaveFile como headerFile
    fileInstance = program.dataFile
    if fileInstance.save == 1:
        errorLog.writeLog("Arquivo já inicializado ")
        return
        
    # arquivo e a variável arquivo recebe o nome que o usuário informa na interface do arquivo a ser criado
    arquivo = ui.lineEdit_FileName.text()
    fileInstance.startDataSave(arquivo)
    fileInstance.writeRow("***\n")
    fileInstance.writeRow("CARRO: " + str(ui.lineEdit_SetupCar.text()) + "\n")
    fileInstance.writeRow("PISTA: " + str(ui.lineEdit_SetupTrack.text()) + "\n")
    fileInstance.writeRow("PILOTO: " + str(ui.lineEdit_SetupDriver.text()) + "\n")
    fileInstance.writeRow("TEMPERATURA AMBIENTE: " + str(ui.lineEdit_SetupTemperature.text()) + "\n")
    fileInstance.writeRow("ANTIROLL: " +str(ui.lineEdit_SetupAntiroll.text()) + "\n")
    fileInstance.writeRow("PRESSAO PNEUS DIANTEIROS: " +str(ui.lineEdit_SetupTirePressureFront.text()) + "\n")
    fileInstance.writeRow("PRESSAO PNEUS TASEIROS: " +str(ui.lineEdit_SetupTirePressureRear.text()) + "\n")
    fileInstance.writeRow("ANGULO DE ATAQUE DA ASA: " +str(ui.lineEdit_SetupWingAttackAngle.text()) + "\n")
    fileInstance.writeRow("MAPA MOTOR: " +str(ui.lineEdit_SetupEngineMap.text()) + "\n")
    fileInstance.writeRow("BALANCE BAR: " +str(ui.lineEdit_SetupBalanceBar.text()) + "\n")
    fileInstance.writeRow("DIFERENCIAL: " +str(ui.lineEdit_SetupDifferential.text()) + "\n")
    fileInstance.writeRow("TAXA DE AQUISICAO: "  + "\n")
    fileInstance.writeRow("COMENTARIOS: " +str(ui.textEdit_SetupComments.toPlainText()) + "\n")
    fileInstance.writeRow("POSICAO MAXIMA DO VOLANTE: " +str(ui.lineEdit_WheelPosMax.text()) + "\n")
    fileInstance.writeRow("POSICAO MINIMA DO VOLANTE: " +str(ui.lineEdit_WheelPosMin.text()) + "\n")
    fileInstance.writeRow("SUSPENSAO: " +str(ui.lineEdit_CalibrationConstant.text()) + "\n")
    fileInstance.writeRow("PACOTE1 " + ui.lineEdit_SampleRate1.text() + ' ' + vectorToString((list(Data.dic.keys())[0:11]), ' '))
    fileInstance.writeRow("PACOTE2 " + ui.lineEdit_SampleRate2.text() + ' ' + vectorToString((list(Data.dic.keys())[12:22]), ' '))
    fileInstance.writeRow("PACOTE3 " + ui.lineEdit_SampleRate3.text() + ' ' + vectorToString((list(Data.dic.keys())[23:37]), ' '))
    fileInstance.writeRow("PACOTE4 " + ui.lineEdit_SampleRate4.text() + ' ' + vectorToString((list(Data.dic.keys())[38:59]), ' '))
    # fileInstance.writeRow("PACOTE1 40 acelY acelX acelZ velDD velT sparkCut suspPos time\n")
    # fileInstance.writeRow("PACOTE2 20 oleoP fuelP tps rearBrakeP frontBrakeP volPos beacon correnteBat rpm time2\n")
    # fileInstance.writeRow("PACOTE3 2 ect batVoltage releBomba releVent pduTemp tempDiscoD tempDiscoE time3\n")
    fileInstance.writeRow("***\n\n")

    ui.label_12.setText("Saving...")  # informa ao usuário a situação atual de gravação de dados


def stopSave(): #!não está em local algum do novo programa
    fileInstance = program.dataFile
    fileInstance.stopSave()
    ui.label_12.setText("Not saving...")  # informa ao usuário a situação atual de gravação de dados


def updatePlot(data): #!localizado em Update
    # as linhas a seguir plotam os gráficos selecionados atráves dos checkBox e define as cores de cada gráfico.
    # Os gráficos são compostos pelos últimos 50 pontos do dado
    # Arrasta vetor pto lado para que novo valor possa ser inserid

    #todo: imagino q tenha q trocar esse arrayTime3 pelo outro Time
    # Atualiza graficos
    ui.graphicsView_EngineData.clear()
    if ui.checkBox_EngineTemperature.isChecked() == 1:
        ui.graphicsView_EngineData.plot(data.arrayTime3, data.arrayTemp, pen='r')
    if ui.checkBox_FuelPressure.isChecked() == 1:
        ui.graphicsView_EngineData.plot(data.arrayTime3, data.arrayFuelP, pen='g')
    if ui.checkBox_Voltage.isChecked() == 1:
        ui.graphicsView_EngineData.plot(data.arrayTime3, data.arrayBattery, pen='b')
    if ui.checkBox_OilPressure.isChecked() == 1:
        ui.graphicsView_EngineData.plot(data.arrayTime3, data.arrayOilP, pen='k')


# Coloca o background da linha da lista na cor color, onde color e do tipo QtGui.QColor(r, g, b)
def setFieldBackground(tableWidget, color, i): #!localizado em Alarms
    for j in range(0, 2):
        item = tableWidget.item(i, j)
        item.setBackground(color)

#todo: tenho q refazer essa porra todinha por causa dos novos alarmes mas to com sono pra cacete agora
# Confere se alarme deve ser ativado e colore background caso seja o caso
def checkAlarm(data, key, tableWidget, i): #!localizado em Alarms
    worring = data.alarms[key][0]
    critical= data.alarms[key][1]
    type = data.alarms[key][2]
    
    #para alarmes 'maior que'
    if type == 'greater than':
        if data.dic[key] > critical:
            setFieldBackground(tableWidget, QtGui.QColor(255, 0, 0), i)
        elif worring != '':
            if data.dic[key] > worring:
                setFieldBackground(tableWidget, QtGui.QColor(255, 255, 0), i)
        else:
            setFieldBackground(tableWidget, QtGui.QColor(255, 255, 255), i)

    #para alarmes 'menor que'
    elif type == 'lesser than':
        if data.dic[key] < critical:
            setFieldBackground(tableWidget,QtGui.QColor(255, 0, 0), i)
        elif worring != '':
            if data.dic[key] < worring:
                setFieldBackground(tableWidget, QtGui.QColor(255, 255, 0), i)
        else:
            setFieldBackground(tableWidget, QtGui.QColor(255, 255, 255), i)

    #para alarmes 'igual a'
    elif type == 'equals':
        if worring != '' and critical != '':
            if data.dic[key] == worring or data.dic[key] == critical:
                setFieldBackground(tableWidget, QtGui.QColor(255, 0, 0), i)
            else:
                setFieldBackground(tableWidget, QtGui.QColor(255, 255, 255), i)


# Função que atualiza os mostradores relacionados aos dados do pacote 1
# Pacote 1: X_Accelerometer, Y_Accelerometer, Z_Accelerometer, Sparcut Relay, Speed, Suspension Course, time
# Para atualizar as células da tabela tableWidget_Package1 é necessário definir o valor da variável item como o
# desejado, definir a formatação, nesse caso centralizado, e inserir na posição (linha, coluna) a variável item
#todo: adicionar os itens adicionados recentemente (spark, velAngular, tempBat) e remover os antigos
def updateP1Interface(data):

    if ui.radioButton_applyFunctions.isChecked(): #!localizado em Update na updatePXInterface
        dataDictionary = data.dic
    else:
        dataDictionary = data.dicRaw

    elements = len(data.packNames[0:11])

    # Itera na variavel que contem a ordem dos pacotes para pegar as respectivas chaves do dicionario
    for key, i in zip(data.packNames[0:11], range(0, elements)):
        # Cria elemento da tabela, faz o alinhamento e coloca valor
        item = QTableWidgetItem(str(dataDictionary[key]))
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui.tableWidget_Package1.setItem(i, 0, item)
        # Alarmes
        if data.alarms[key] != []:
            checkAlarm(data, key, ui.tableWidget_Package1, i)
        else:
            setFieldBackground(ui.tableWidget_Package1, QtGui.QColor(255, 255, 255), i)

    # print(data.dic['acelX'])

    update_diagramagg(data)  # Chamada da função update_diagramagg


# Função que atualiza os mostradores relacionados aos dados do pacote 2
def updateP2Interface(data):

    if ui.radioButton_applyFunctions.isChecked():
        dataDictionary = data.dic
    else:
        dataDictionary = data.dicRaw

    elements = len(data.packNames[12:22])
    for key, i in zip(data.packNames[12:22], range(0, elements)):
        item = QTableWidgetItem(str(dataDictionary[key]))
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui.tableWidget_Package2.setItem(i, 0, item)

        if data.alarms[key] != []:
            checkAlarm(data, key, ui.tableWidget_Package2, i)
        else:
            setFieldBackground(ui.tableWidget_Package2, QtGui.QColor(255, 255, 255), i)


# Função que atualiza os mostradores relacionados aos dados do pacote 3
def updateP3Interface(data):

    if ui.radioButton_applyFunctions.isChecked():
        dataDictionary = data.dic
    else:
        dataDictionary = data.dicRaw

    elements = len(data.packNames[23:37])
    for key, i in zip(data.packNames[23:37], range(0, elements)):
        item = QTableWidgetItem(str(dataDictionary[key]))
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui.tableWidget_Package3.setItem(i, 0, item)

        if data.alarms[key] != []:
            checkAlarm(data, key, ui.tableWidget_Package3, i)
        else:
            setFieldBackground(ui.tableWidget_Package3, QtGui.QColor(255, 255, 255), i)

    if ((data.dic['rearBrakeP'] + data.dic['frontBrakeP']) != 0):  # Verificação necessária para que não ocorra divisão por zero
        ui.progressBar_FrontBrakeBalance.setValue(100 * data.dic['frontBrakeP'] / (data.dic['rearBrakeP'] + data.dic['frontBrakeP']))  # porcentagem da pressão referente ao freio dianteiro
        ui.progressBar_RearBrakeBalance.setValue(100 * data.dic['rearBrakeP'] / (data.dic['rearBrakeP'] + data.dic['frontBrakeP'])) # traseiro

    # atualiza gauges
    ui.progressBar_FrontBreakPressure.setValue(data.dic['frontBrakeP'])
    ui.label_65.setText(str(data.dic['frontBrakeP']))
    ui.label_69.setText(str(data.dic['rearBrakeP']))
    # distribuicao dos freios
    ui.progressBar_RearBreakPressure.setValue(data.dic['rearBrakeP'])


    ui.progressBar_FuelPressure.setValue(data.dic['fuelP'])
    ui.label_17.setText(str(data.dic['fuelP']))

    ui.progressBar_OilPressure.setValue(data.dic['oleoP'])
    ui.label_10.setText(str(data.dic['oleoP']))

    ui.progressBar_TPS.setValue(data.dic['tps'])
    ui.progressBar_TPS.setProperty("value", data.dic['tps'])

    ui.dial_WheelPos.setValue(data.dic['volPos'])
    ui.label_19.setText(str(data.dic['volPos']))

    updatePlot(data)


# Função que atualiza os mostradores relacionados aos dados do pacote 4
def updateP4Interface(data):

    if ui.radioButton_applyFunctions.isChecked():
        dataDictionary = data.dic
    else:
        dataDictionary = data.dicRaw

    elements = len(data.packNames[38:59])
    for key, i in zip(data.packNames[38:59], range(0, elements)):
        item = QTableWidgetItem(str(dataDictionary[key]))
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        ui.tableWidget_Package4.setItem(i, 0, item)

        if data.alarms[key] != []:
            checkAlarm(data, key, ui.tableWidget_Package4, i)
        else:
            setFieldBackground(ui.tableWidget_Package4, QtGui.QColor(255, 255, 255), i)

    # Gauge da bateria
    ui.progressBar_BatteryVoltage.setValue(int(data.dic['batVoltage']))
    ui.label_15.setText(str(data.dic['batVoltage']))

  # alarme bateria: o fundo da linha da tabela referente à tensão na bateria recebe a cor vermelha
    """if (data.dic['batVoltage'] <= 11.5):
        item = ui.tableWidget_Package3.item(0, 0)
        item.setBackground(QtGui.QColor(255, 0, 0))
        item = ui.tableWidget_Package3.item(0, 2)
        item.setBackground(QtGui.QColor(255, 0, 0))
        item = ui.tableWidget_Package3.item(0, 1)
        item.setBackground(QtGui.QColor(255, 0, 0))
    else:
        item = ui.tableWidget_Package3.item(0, 0)
        item.setBackground(QtGui.QColor(255, 255, 255))
        item = ui.tableWidget_Package3.item(0, 2)
        item.setBackground(QtGui.QColor(255, 255, 255))
        item = ui.tableWidget_Package3.item(0, 1)
        item.setBackground(QtGui.QColor(255, 255, 255))"""

    ui.progressBar_EngineTemperature.setValue(data.dic['ect'])
    ui.label_6.setText(str(data.dic['ect']))

    # alarme temperatura: o fundo da linha da tabela referente à temperatura do motor recebe a cor vermelha
    """if (data.dic['ect'] >= 95.0):
        item = ui.tableWidget_Package3.item(3, 0)
        item.setBackground(QtGui.QColor(255, 0, 0))
        item = ui.tableWidget_Package3.item(3, 2)
        item.setBackground(QtGui.QColor(255, 0, 0))
        item = ui.tableWidget_Package3.item(3, 1)
        item.setBackground(QtGui.QColor(255, 0, 0))
    else:
        item = ui.tableWidget_Package3.item(3, 0)
        item.setBackground(QtGui.QColor(255, 255, 255))
        item = ui.tableWidget_Package3.item(3, 2)
        item.setBackground(QtGui.QColor(255, 255, 255))
        item = ui.tableWidget_Package3.item(3, 1)
        item.setBackground(QtGui.QColor(255, 255, 255))"""

    if (int(data.dicRaw['releVent']) == 1):
        ui.radioButton_FanRelay.setChecked(False)
    else:
        ui.radioButton_FanRelay.setChecked(True)

    if (int(data.dicRaw['releBomba']) == 1):
        ui.radioButton_FuelPumpRelay.setChecked(False)
    else:
        ui.radioButton_FuelPumpRelay.setChecked(True)

    updatePlot(data)

#todo: estudar diagrama GG e alterar isso
# função que atualiza o diagrama gg
def update_diagramagg(data):
    ui.graphicsView_DiagramaGG.clear()
    ui.graphicsView_DiagramaGG.plot([data.dic['acelX_DD']], [data.dic['acelY_DD']], pen=None, symbol='o')


#!essa classe teve alterações extras por causa do novo alarme, talvez de bugs
def saveAlarm(): #!localizado em Alarms
    global settings
    #associa campos da interface a variaveis
    key = ui.alarmComboBox.currentText()
    type = ui.alarmTypeComboBox.currentText()
    valWorrying = ui.alarmlineEdit.text()
    valCritical = ui.alarmlineEdit_2.text()

    #caso não tenha inserido o tipo do alarme, ele não é salvo
    if (type == ''):
        if settings.contains('alarm'+key):
            settings.remove('alarm'+key)
        program.data.alarms[key] = []

    #salva alarme somente com valor preocupante inserido
    elif (valWorrying != '' and valCritical == ''):
        store = [float(valWorrying),'', type]
        settings.setValue('alarm' + key, store)
        program.data.alarms[key] = store
        displayAlarm()

    #salva alarme somente com valor critico inserido
    elif (valWorrying == '' and valCritical != ''):
        store = ['',float(valCritical), type]
        settings.setValue('alarm' + key, store)
        program.data.alarms[key] = store
        displayAlarm()

    #salva alarme com os dois valores inserido
    else:
        store = [float(valWorrying), float(valCritical), type]
        settings.setValue('alarm' + key, store)
        program.data.alarms[key] = store
        displayAlarm() #?adição da carol, n sei se funciona mas ok


# Chama funcao que reseta alarms dentro da instancia de Data em program e reseta settings
def setDefaultAlarms(): #!localizado em Alarms
    global settings
    program.data.setDefaultAlarms()
    for key in program.data.alarms:
        if settings.contains('alarm'+key):
            settings.remove('alarm'+key)

#todo: tenho que conferir aqui as mundancas de indice q a carol fez q eu n entendi nada
# Funcao responsavel por atualizar os campos na parte de configuracao dos alarmes.
# Ela é chamada qnd o usuario escolhe algum dado no comboBox dos alarmes
def displayAlarm(types): #!localizado em Alarms

    # Pega qual dado esta selecionado no combobox e acessa dicionario de Data
    text = ui.alarmComboBox.currentText()
    val = program.data.alarms[text]
    # Caso o alarme exista, mostra ele no campo tipo e valor
    if val != []:
        index = types.index(val[2])
        ui.alarmlineEdit.setText(str(val[0]))
        ui.alarmlineEdit_2.setText(str(val[1]))
        ui.alarmTypeComboBox.setCurrentIndex(index)
    else:
        ui.alarmlineEdit.setText('')
        ui.alarmlineEdit_2.setText('')
        ui.alarmTypeComboBox.setCurrentIndex(0)


# função para atualizar settings com novos valores de setup
def saveSetup(): #!localizado em Setup
    global settings, errorLog
    settings.setValue('wheelPosMax',str(ui.lineEdit_WheelPosMax.text()))
    settings.setValue('wheelPosMin',str(ui.lineEdit_WheelPosMin.text()))
    settings.setValue('calibConstant',str(ui.lineEdit_CalibrationConstant.text()))
    settings.setValue('setupCar',str(ui.lineEdit_SetupCar.text()))
    settings.setValue('setupTrack' ,str(ui.lineEdit_SetupTrack.text()))
    settings.setValue('setupDriver' ,str(ui.lineEdit_SetupDriver.text()))
    settings.setValue('setupTemp' ,str(ui.lineEdit_SetupTemperature.text()))
    settings.setValue('setupAntiroll' ,str(ui.lineEdit_SetupAntiroll.text()))
    settings.setValue('tirePFront' ,str(ui.lineEdit_SetupTirePressureFront.text()))
    settings.setValue('tirePRear' ,str(ui.lineEdit_SetupTirePressureRear.text()))
    settings.setValue('aeroAngle' ,str(ui.lineEdit_SetupWingAttackAngle.text()))
    settings.setValue('engineMap' ,str(ui.lineEdit_SetupEngineMap.text()))
    settings.setValue('balanceBar' ,str(ui.lineEdit_SetupBalanceBar.text()))
    settings.setValue('setupDrexler' ,str(ui.lineEdit_SetupDifferential.text()))
    settings.setValue('setupComments' ,str(ui.textEdit_SetupComments.toPlainText()))
    settings.setValue('filename', ui.lineEdit_FileName.text())
    settings.setValue('sampleRate1', ui.lineEdit_SampleRate1.text())
    settings.setValue('sampleRate2', ui.lineEdit_SampleRate2.text())
    settings.setValue('sampleRate3', ui.lineEdit_SampleRate3.text())
    settings.setValue('sampleRate4', ui.lineEdit_SampleRate4.text())

#!esta função foi comentada/removida no remake da carol. Testar o pq
# Abre dialogo para escolher arquivo
def selectFile(): #!localizado em SaveFile
    fileName, _ = QtWidgets.QFileDialog.getOpenFileName(MainWindow, "Escolha arquivo .txt",
                                                        "", "All Files (*);;Text Files (*.txt)")

    if len(fileName) > 5:
        ui.lineEdit_FileName.setText(fileName)
        return fileName
    else:
        return


def logEnabled(): #!localizado em Log
    global errorLog, bufferLog
    if ui.radioButton_errorLog.isChecked():
        errorLog.on = 'on'
    else:
        errorLog.on = 'off'

    if ui.radioButton_bufferLog.isChecked():
        bufferLog.on = 'on'
    else:
        bufferLog.on = 'off'


#Método que verifica se atualização da interface está ativada pelo usuário
def updateInterfaceEnabled(): #!localizado em update
    global program 
    if ui.radioButton_updateInterface.isChecked():
        program.updateInterfaceEnabled = True
        print('Ativou Interface')
    else:
        program.updateInterfaceEnabled = False
        print('Desativou Interface')

def exit(): #!localizado em interface20
    #if(Web_App.isRunning): #todo:verificar isso com a nova classe do webApp
    #    Web_App.stop()
    sys.exit(app.exec_())

#todo: ajustar td daqui pra frente. provavelmente 90% disso ta em interface20
# settings armazena os campos de configuracao na interface
settings = QtCore.QSettings('testa', 'interface_renovada') #!localizado em interface20

# Roda janela
app = QtWidgets.QApplication(sys.argv)
app.setStyle("fusion")
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
#MainWindow.show() #?n sei, ta no novo

# Classes globais
#Instancia para erros gerais
errorLog = Log(ui.errorLog, maxElements=70)

#Instancia para erros no buffer de dado
bufferLog = Log(ui.textBrowser_Buffer, maxElements=15)
logEnabled()

# updateInterfaceFunctions é um dicionario que contem algumas funcoes de atualizacao da interface
# ele é passado como parametro na criacao da classe program, para que essas funcoes possam ser chamadas por ela
updateInterfaceFunctions = {1: updateP1Interface, 2: updateP2Interface, 3: updateP3Interface, 4: updateP4Interface, 'updatePlot': updatePlot}
program = Program(ui.doubleSpinBox_UpdateTime.value() * 1000, errorLog, bufferLog, updateInterfaceFunctions)#, updateCounterMax=[6, 3,0,3])
updateConstants()


ui.pushButton_SaveFile.clicked.connect(beginDataSave)  # botão para iniciar gravação de dados no txt
ui.pushButton_StopSaveFile.clicked.connect(stopSave)  # botão para parar a gravação de dados txt
ui.pushButton_PauseProgram.clicked.connect(program.stopProgram)  # botão para pausar o programa
ui.restoreDefaultAlarmPushButton.clicked.connect(setDefaultAlarms)


ui.lineEdit_WheelPosMin.editingFinished.connect(updateConstants)
ui.lineEdit_WheelPosMax.editingFinished.connect(updateConstants)
ui.updateCounterP1.valueChanged.connect(updateConstants)
ui.updateCounterP2.valueChanged.connect(updateConstants)
ui.updateCounterP3.valueChanged.connect(updateConstants)
ui.updateCounterP4.valueChanged.connect(updateConstants)

# ações
ui.pushButton_Exit.clicked.connect(exit)  # botão para fechar a interface
ui.pushButton_StartProgram.clicked.connect(startProgram)  # botão para iniciar o programa
ui.pushButton_UpdatePorts.clicked.connect(updatePorts)  # botão para atualizar as portas seriis disponíveis
ui.pushButton_SaveSetupValues.clicked.connect(saveSetup)  # botão para atualizar os dados de setup no arquivo txt
ui.saveAlarmPushButton.clicked.connect(saveAlarm)
ui.actionExit.triggered.connect(exit)  # realiza a ação para fechar a interface

ui.radioButton_errorLog.toggled.connect(logEnabled)
ui.radioButton_bufferLog.toggled.connect(logEnabled)
ui.radioButton_updateInterface.toggled.connect(updateInterfaceEnabled)


ui.comboBox_SerialPorts.addItems(listSerialPorts())  # mostra as portas seriais disponíveis
ui.comboBox_Baudrate.addItems(["115200", "38400", "1200", "2400", "9600", "19200", "57600" ])  # mostra os baudrates disponíveis
#ui.comboBox_Baudrate.currentIndexChanged.connect(selection_baudrate)
#pixmap = QPixmap("image1.png")
#ui.label_28.setPixmap(pixmap)
loadSetup()  # inicializa os valores de setup de acordo com o arquivo setup
ui.label_12.setText("Not saving...")  # informa na interface que os dados não estão sendo salvos

# Range ggs
ui.graphicsView_DiagramaGG.setXRange(-2, 2)
ui.graphicsView_DiagramaGG.setYRange(-2, 2)

# cores do gráfico
ui.checkBox_OilPressure.setStyleSheet('color:blue')
ui.checkBox_FuelPressure.setStyleSheet('color:green')
ui.checkBox_EngineTemperature.setStyleSheet('color:red')
ui.checkBox_OilPressure.setStyleSheet('color:black')

ui.alarmComboBox.addItems(program.data.alarms)
alarmTypes = ['', 'greater than', 'lesser than', 'equal to']
ui.alarmComboBox.activated.connect(lambda: displayAlarm(alarmTypes))
ui.alarmTypeComboBox.addItems(alarmTypes)

# Mostra a janela e fecha o programa quando ela é fechada (?)
MainWindow.show()
sys.exit(app.exec_())
