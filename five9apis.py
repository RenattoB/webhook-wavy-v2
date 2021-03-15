import json
import requests
import asyncio
from log import *


#Creacion de token
def five9GetToken():   
    log('***Generando token con API de five9***\n')
    url = 'https://app-scl.five9.com:443/appsvcs/rs/svc/auth/anon?cookieless=true'
    data = json.dumps({"tenantName": "Telectronic Reseller"})
    headers = {'Content-Type': 'application/json'}
    log(f'url: {url}\n')
    log(f'Json para generar la conversación: {data}\n')
    log(f'Headers: {headers}\n')
    response = requests.post(url, data = data, headers = headers)
    log(f'Codigo de respuesta de la API generar token: {response.status_code}\n')
    return response.json()['tokenId']

#Crear el json de una conversacion nueva
def createConversationJson(data):
    messageText = data['data'][0]['message']['messageText']
    userNumber = data['data'][0]['source']
    userName = data['data'][0]['userProfile']['name']
    wavyMessageId = data['data'][0]['id']

    cJson ={ "campaignName": "test_campaing_02",
    "tenantId": 129497,
    "externalId": f"{userNumber}",
    "type": "RCS",
    "contact": {
        "state": "CA",
        "zip": "94568",
        "city": "Pleasanton",
        "street": "ABC",
        "company": "Demo Company",
        "firstName": f"{userName}",
        "lastName": "-",
        "gender": "Male",
        "number1": f"{userNumber}",
        "number2": "-",
        "number3": "-",
        "socialAccountHandle": "A",
        "socialAccountName": "B",
        "socialAccountImageUrl": "URLA",
        "socialAccountProfileUrl": "URLB"
        },
    "priority": 12345,
    "callbackUrl": "https://tll-web-hook.azurewebsites.net/web-hook",
    "attributes": {
        "question": f"{messageText}",
        "Custom.external_history": "Hello"
            }
        }    

    return cJson

#Logica para crear nuevas conversasiones
def createConversation(tokenId, cJson):
    log('***Creando conversación con API de five9***\n')
    url = 'https://app-atl.five9.com:443/appsvcs/rs/svc/conversations'    
    data = cJson    
    headers = {'Content-Type': 'application/json', 'Authorization' : f'Bearer-{tokenId}', 'farmId' : '3000000000000000021'}
    log(f'url: {url}\n')
    log(f'Json para generar la conversación: {data}\n')
    log(f'Headers: {headers}\n')
    response = requests.post(url, data = json.dumps(data), headers = headers)
    log(f'Código de respuesta de la API: {response.status_code}\n')

def validateSession(tokenId):
    try: 
        log('***Validando sesión con la API de five9***\n')
        url = f'https://app-atl.five9.com:443/appsvcs/rs/svc/conversations/{tokenId}/info'
        headers = {'Authorization' : f'Bearer-{tokenId}', 'farmId' : '3000000000000000021'}
        log(f'url: {url}\n')
        log(f'Headers: {headers}\n')
        response = requests.get(url, headers = headers)
        log(f'Código de respuesta de la API: {response.status_code}\n')
        return response.json()['status']
    except:
        log ('Error en validate session\n')
        return 'FAILED'


#Logica para mandar mensajes a tokenIds activos
def sendMessage(tokenId, data):
    log('***Mandando mensaje con la API de five9***\n')
    messageText = data['data'][0]['message']['messageText']
    url = f'https://app-atl.five9.com:443/appsvcs/rs/svc/conversations/{tokenId}/messages'
    headers = {'Content-Type': 'application/json', 'Authorization' : f'Bearer-{tokenId}', 'farmId' : '3000000000000000021'}
    message = {'message' : f'{messageText}'}
    log(f'url: {url}\n')
    log(f'Json para el envio de mensaje: {message}\n')
    log(f'Headers: {headers}\n')
    response = requests.post(url, data = json.dumps(message), headers = headers)
    log(f'Código de respuesta de la API: {response.status_code}\n')

def five9Status(data, tokenId):
    log('Validando mensaje enviado por asesor\n')    
    messageId = data['data'][0]['correlationId'] #Mensaje a validar        
    url = f'https://app-atl.five9.com:443/appsvcs/rs/svc/conversations/{tokenId}/messages/acknowledge'
    headers = {'Content-Type': 'application/json', 'Authorization' : f'Bearer-{tokenId}', 'farmId' : '3000000000000000021'}
    cjson = { "messages":[{
                "type" : "DELIVERED",
                "messageId" : f"{messageId}"
                }
            ]
        }
    response = requests.put(url, json.dumps(cjson), headers = headers)
    log(f'Codigo de respuesta del Aknowledge message {response.status_code}\n')
    print(log('Terminando interaccion'))
   





