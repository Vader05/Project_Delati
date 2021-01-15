# -*- coding: utf-8 -*-

import psycopg2
from configuration import *
import webscraping_computrabajo
import webscraping_indeed
from controller import Controller
from dbconnection import Connection

'''
def construir_busqueda_filtro(carga, filtro):
    carga["busqueda"] = filtro
    busqueda = ""
    if carga["busqueda"] is not None:
        busqueda = "-busqueda-" + carga["busqueda"].replace(" ", "-")

    busqueda_area = ""
    if carga["busqueda_area"] not in ("", None):
        busqueda_area = "-area-" + carga["busqueda_area"].replace(" ", "-")

    total = ""
    if busqueda == "" and busqueda_area == "":
        total = ""
    carga["url_principal"] = WS_PORTAL_LABORAL_URL
    urlbusqueda = "/trabajo-de-analista-programador-en-lima?q=analista%20programador"
    paginado = "&p="

    extension = ""
    ordenado = ""
    carga["url_prefix"] = carga["url_principal"] + urlbusqueda + paginado
    carga["url_sufix"] = extension + ordenado

    carga["url_pagina"] = carga["url_principal"]
    carga["url_busqueda"] = urlbusqueda
'''
#construyendo url de busqueda computrabajo
def url_busqueda_computrabajo(filtro):
    busqueda = "trabajo-de-" + filtro.replace(" ", "-")+"-en-lima?q="+filtro.replace(" ","%20")
    return busqueda

def set_url_busqueda_indeed(carga):
    #URL DE PORTAL DELATI
    carga["url_principal"] = INDEED["WS_PORTAL_LABORAL_URL"]
    urlbusqueda = "/jobs?q=Analista+programador&l=Lima"
    paginado = "&start="

    carga["url_prefix"] = carga["url_principal"] + urlbusqueda + paginado
    carga["url_sufix"] = ""
    carga["url_busqueda"] = carga["url_principal"] + urlbusqueda

def set_url_busqueda_compuTrabajo(carga):
    #MODIFICADO URL COMPU-TRABAJO
    carga["url_principal"] = COMPUTRABAJO["WS_PORTAL_LABORAL_URL"]
    urlbusqueda = "/trabajo-de-analista-programador-en-lima?q=analista%20programador"
    paginado = "&p="
    carga["url_prefix"] = carga["url_principal"] + urlbusqueda + paginado
    carga["url_sufix"] = ""
    carga["url_busqueda"] = carga["url_principal"] + urlbusqueda

#retorna el url de las palabras clave para todos los portales
def set_url_busqueda_gozu(carga, sitio, filtro):
    #MODIFICADO URL COMPU-TRABAJO
    carga["url_principal"] = sitio["WS_PORTAL_LABORAL_URL"]
    urlbusqueda = url_busqueda_computrabajo(filtro)
    paginado = sitio["PAGINADO"]
    carga["url_prefix"] = carga["url_principal"] + urlbusqueda + paginado
    carga["url_sufix"] = ""
    carga["url_busqueda"] = carga["url_principal"] + urlbusqueda

def connect_bd():
    con = Connection(DATABASE["DB_HOST"], DATABASE["DB_SERVICE"], DATABASE["DB_USER"], DATABASE["DB_PASSWORD"])
    con.connect()
    return con

def delati_compuTrabajo():
    controller = Controller()
    con = connect_bd()
    palabras= controller.getwords(con)
    for filtro in palabras:
        carga = {}
        carga["pagina"] = COMPUTRABAJO["WS_PORTAL_LABORAL"]
        carga["cant_paginas"] = COMPUTRABAJO["WS_PAGINAS"]
        carga["pagina_inicial"] = COMPUTRABAJO["WS_PAGINA_INICIAL"]
        carga["cant_ofertas"] = COMPUTRABAJO["WS_OFERTAS"]
        carga["busqueda_area"] = COMPUTRABAJO["WS_AREA"]
        carga["busqueda"] = ""
        carga["id_keyword"]=filtro[0]
        #set_url_busqueda_compuTrabajo(carga)
        set_url_busqueda_gozu(carga, COMPUTRABAJO, filtro[1])
        carga["id_carga"] = controller.registrar_webscraping(con, carga)
        '''
        listaOferta = webscraping_computrabajo.scraping_ofertas(con, carga["url_principal"], carga["url_prefix"], carga["url_sufix"],
                                                carga["pagina_inicial"], carga["cant_paginas"], carga["cant_ofertas"],
                                                carga["id_carga"])
        '''
        #print(listaOferta)

def delati_indeed():
    controller = Controller()
    con = connect_bd()
    carga = {}
    carga["pagina"] = INDEED["WS_PORTAL_LABORAL"]
    carga["cant_paginas"] = INDEED["WS_PAGINAS"]
    carga["pagina_inicial"] = INDEED["WS_PAGINA_INICIAL"]
    carga["cant_ofertas"] = INDEED["WS_OFERTAS"]
    carga["busqueda_area"] = INDEED["WS_AREA"]
    carga["busqueda"] = ""
    set_url_busqueda_indeed(carga)
    carga["id_carga"] = controller.registrar_webscraping(con, carga)

    listaOferta = webscraping_indeed.scraping_ofertas(con, carga["url_principal"], carga["url_prefix"], carga["url_sufix"],
                                               carga["pagina_inicial"], carga["cant_paginas"], carga["cant_ofertas"],
                                               carga["id_carga"])
    print(listaOferta)

if __name__ == "__main__":
    delati_compuTrabajo()
    #delati_indeed()

