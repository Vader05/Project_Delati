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

def connect_bd():
    con = Connection(DATABASE["DB_HOST"], DATABASE["DB_SERVICE"], DATABASE["DB_USER"], DATABASE["DB_PASSWORD"])
    con.connect()
    return con

def delati_compuTrabajo():
    controller = Controller()
    con = connect_bd()
    carga = {}
    carga["pagina"] = COMPUTRABAJO["WS_PORTAL_LABORAL"]
    carga["cant_paginas"] = COMPUTRABAJO["WS_PAGINAS"]
    carga["pagina_inicial"] = COMPUTRABAJO["WS_PAGINA_INICIAL"]
    carga["cant_ofertas"] = COMPUTRABAJO["WS_OFERTAS"]
    carga["busqueda_area"] = COMPUTRABAJO["WS_AREA"]
    carga["busqueda"] = ""
    set_url_busqueda_compuTrabajo(carga)
    carga["id_carga"] = controller.registrar_webscraping(con, carga)
    listaOferta = webscraping_computrabajo.scraping_ofertas(con, carga["url_principal"], carga["url_prefix"], carga["url_sufix"],
                                               carga["pagina_inicial"], carga["cant_paginas"], carga["cant_ofertas"],
                                               carga["id_carga"])
    print(listaOferta)

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
    delati_indeed()

