from flask import Flask, request, Response
import json
from five9apis import *
from bd import *
import threading
from log import *

app = Flask(__name__)


@app.route('/webhook-wavy', methods = ['POST'])
def wavyMessage():
    log('***Iniciando webhook wavy***\n')
    if 'application/json' in request.headers['content-type']:
            message = request.json
            log(f'Json devuelto: \n{message}\n')            
    else:
        log(f'El body mandado no es de tipo JSON\n')
        return Response(status = 415)

    valid = processJson(message)
    if not valid:
        log(f'El JSON no es valido\n')
    else:
        thread =threading.Thread(target = typeCheck, args = (message, ))
        log(f'***Comenzando hilo para five9***\n')
        thread.start()
        log(f'***Se responde a la api de Wavy con Status code de 200***\n')
        return Response(status = 200)  
    
#Procesamos que el json sea valido
def processJson(message):
    if 'data' in message:
        return True
    else:
        return False 

#Procesamos que tipo de json estamos tradando
def typeCheck(data):
    if 'message' in data['data'][0]:
        messageType = data['data'][0]['message']['type']
        processMO(messageType, data)
    else:
        processStatus(data)

#Logica para el json de actualizacion de estado
def processStatus(data):
    log('Se recibio una petición de actualización de callback\n')
    status = data['data'][0]['sentStatus']
    if status == 'SENT_SUCCESS':
        number =  data['data'][0]['destination']
        listToken = searchUser(number)
        tokenId = listToken[0]
        if not listToken[1]:
            vSession = validateSession(tokenId) 
            if vSession == 'ACTIVE': 
                log('Sesion activa, validando estado de mensaje a delivered\n')
                five9Status(data, tokenId)
            else:
                print(log('Sesion terminada..., no se valida nada\n'))
        else:
            print(log('Usuario nuevo, no se valida nada...'))
    else:
        print(log('Estado de mensaje no enviado...\n'))


#Logica para el json de MO
def processMO(messageType, data):
    log('Se recibio una interacción de MO\n')
    number = data['data'][0]['source']
    if messageType == 'TEXT':
        log('Se recibio un MO de tipo TEXT\n')
        listToken = searchUser(number)
        tokenId = listToken[0]
        #True = Usuario Nuevo
        if listToken[1]:
            log('Creando conversación para usuario nuevo\n\n')
            cJson = createConversationJson(data)
            createConversation(tokenId, cJson)
            print(log('***Finalización del hilo del webhook***\n\n'))  
        else:
            log('Logica de sesion activa, validando el estado de la sesion...\n\n') 
            vSession = validateSession(tokenId)  
            log(f'El estado de la sesion es {vSession}\n') 
            if vSession == 'TERMINATED' or vSession == 'FAILED':
                log('Sesion terminada generando nuevo token\n\n')
                tokenId = five9GetToken()
                updateTokeId(tokenId, number)
                log('Creando nueva sesion de conversación\n\n')
                cJson = createConversationJson(data)
                createConversation(tokenId, cJson)
                print(log('***Finalización del hilo del webhook***\n\n'))     
            else:
                log(f'Conversación con el tokenId : {tokenId} activa, enviando mensaje a Agente\n\n') 
                sendMessage(tokenId, data)
                print(log('***Finalización del hilo del webhook***\n\n'))  
    else:
        log('Se recibio un MO diferente de tipo texto, actualmente no soportado por la versión de webhook\n')



if __name__ == '__main__':
    app.run()