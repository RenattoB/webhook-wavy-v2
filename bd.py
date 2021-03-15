import pandas as pd
from app import *
from tabulate import tabulate
from five9apis import five9GetToken

bd = pd.DataFrame(columns = ['celular', 'tokenid'])

#Funcion para buscar el token id de un usuario
def searchUser(number):  
    log('***Empezando la busqueda del usuario en el DataFrame local***\n')
    log(f'DataFrame Actual: \n {bd.to_markdown()}\n\n')
    newUser = True
    userExist = bd.loc[bd.celular == number]
    log(f'TokenId encontrado con el numero {number}: \n {userExist.to_markdown()}\n\n')
    if not userExist.empty:        
        tokenid = userExist.tokenid.values[0]
        newUser = False
        log(f'Se encontro a un tokeId relacionado con ese numero, tokenId: {tokenid}\n')
    else:
        log('No se encontro ningun tokenId relacionado con ese numero, generando uno...\n\n')
        tokenid = five9GetToken()
        insertarTokenId(number, tokenid)        
        log(f'Token generado y insertado al Dataframe con exito: {tokenid}\n')
    return [tokenid, newUser]

#Funcion para insertar numero con token id en la BD
def insertarTokenId(number, tokenid):
    bd.loc[len(bd.index)] = [number, tokenid]
    log(f'Numero y token insertados con exito, DataFrame: \n {bd.to_markdown()}\n\n')

def updateTokeId(tokenId, number):
    log(f'Modificando el tokenId para el numero {number}\n')
    bd.loc[bd.celular == number, ['tokenid']] = tokenId
    log(f'DataFrame Modificado: \n {bd.to_markdown()}\n\n')
