# -*- coding: utf-8 -*-

from configuration import *
import webscraping_computrabajo
import webscraping_indeed
from controller import Controller
from dbconnection import Connection
from dboperation import DatesDB
import datetime
import webscraping_buscojobs

#JOSEF
def set_url_busqueda_buscojobs(carga):
    #MODIFICADO URL BUSCOJOBS
    carga["url_principal"] = BUSCOJOBS["WS_PORTAL_LABORAL_URL"]
    #urlbusqueda = "/ofertas/tc25/trabajo-de-tecnologias-de-la-informacion"
    carga["paginado"] = "/"
    #carga["url_prefix"] = carga["url_principal"] + urlbusqueda + paginado
    carga["url_sufix"] = ""
    #carga["url_busqueda"] = carga["url_principal"] + urlbusqueda    


#construyendo url de busqueda computrabajo con filtro en lima
def url_busqueda_computrabajo(filtro):
    #busqueda = "trabajo-de-" + filtro.replace(" ", "-")+"-en-lima?q="+filtro.replace(" ","%20")
    busqueda = "trabajo-de-" + filtro.replace(" ", "-")+"?q="+filtro.replace(" ","%20")
    return busqueda

#construyendo url busqueda indeed con filtro en lima
def url_busqueda_indeed(filtro):
    #/jobs?q=Analista+programador&l=
    busqueda = "/jobs?q=" + filtro.replace(" ", "+")+"&l="
    return busqueda

#retorna las url de la busqueda con palabras clave para todos los portales
#carga: diccionario de sitio web
#sitio: diccionario del sitio web del archivo configuracion
#fitro: palabra clave de busqueda
def set_url_busqueda(carga, sitio, filtro):
    #MODIFICADO URL COMPU-TRABAJO
    carga["url_principal"] = sitio["WS_PORTAL_LABORAL_URL"]
    if sitio["WS_PORTAL_LABORAL"]=="indeed":
        urlbusqueda = url_busqueda_indeed(filtro)
    elif sitio["WS_PORTAL_LABORAL"]=="computrabajo":
        urlbusqueda = url_busqueda_computrabajo(filtro)

    paginado = sitio["PAGINADO"]
    carga["url_prefix"] = carga["url_principal"] + urlbusqueda + paginado
    carga["url_sufix"] = ""
    carga["url_busqueda"] = carga["url_principal"] + urlbusqueda

#metodo para la conxión a la DB
def connect_bd():
    con = Connection(DATABASE["DB_HOST"], DATABASE["DB_SERVICE"], DATABASE["DB_USER"], DATABASE["DB_PASSWORD"])
    con.connect()
    return con

#metodo para llegar carga e insertar en la base de datos
#sitio: diccionario del sitio web del acrhivo de configuración
def delati_portal(sitio):
    controller = Controller()
    con = connect_bd()
    #filtro es una tupla con id y descripcion de la tabla keyword_search
    palabras= controller.getwords(con)
    for filtro in palabras:
        print("\033[1;30m"+'ID_KEYWORD: '+ str(filtro[0]) + ' - PALABRA A ANALIZAR: '+ str(filtro[1]))
        carga = {}
        carga["pagina"] = sitio["WS_PORTAL_LABORAL"]
        carga["cant_paginas"] = sitio["WS_PAGINAS"]
        carga["pagina_inicial"] = sitio["WS_PAGINA_INICIAL"]
        carga["cant_ofertas"] = sitio["WS_OFERTAS"]
        carga["busqueda_area"] = sitio["WS_AREA"]
        carga["busqueda"] = ""
        carga["id_keyword"]=filtro[0]
        #asigna url de busqueda con filtro a carga 
        set_url_busqueda(carga, sitio, filtro[1])
        #registra pagina en tabla webscraping y retorna su id
        carga["id_carga"] = controller.registrar_webscraping(con, carga)
        if sitio["WS_PORTAL_LABORAL"]=="computrabajo":
            #inserta avisos en la tabla oferta y oferta_detalle
            listaOferta = webscraping_computrabajo.scraping_ofertas(con, carga["url_principal"], carga["url_prefix"], carga["url_sufix"],
                                                    carga["pagina_inicial"], carga["cant_paginas"], carga["cant_ofertas"],
                                                    carga["id_carga"])
        elif sitio["WS_PORTAL_LABORAL"]=="indeed":
            listaOferta = webscraping_indeed.scraping_ofertas(con, carga["url_principal"], carga["url_prefix"], carga["url_sufix"],
                                                    carga["pagina_inicial"], carga["cant_paginas"], carga["cant_ofertas"],
                                                    carga["id_carga"])
    print("fin de filtro")


#JOSEF
def delati_buscojobs():
    controller = Controller()
    con = connect_bd()
    carga = {}
    carga["pagina"] = BUSCOJOBS["WS_PORTAL_LABORAL"]
    carga["cant_paginas"] = BUSCOJOBS["WS_PAGINAS"]
    carga["pagina_inicial"] = BUSCOJOBS["WS_PAGINA_INICIAL"]
    carga["cant_ofertas"] = BUSCOJOBS["WS_OFERTAS"]
    carga["busqueda_area"] = BUSCOJOBS["WS_AREA"]
    carga["delati_team"] = BUSCOJOBS["NAME_TEAM"]
    carga["busqueda"] = ""
    set_url_busqueda_buscojobs(carga)

    for type_search in webscraping_buscojobs.obtener_lista_keywords(con):
        carga["url_prefix"] = carga["url_principal"] + type_search['descripcion'] + carga["paginado"]
        carga["url_busqueda"] = carga["url_principal"] + type_search['descripcion']

        carga["id_keyword"] = type_search['id']
        carga["id_carga"] = controller.registrar_webscraping(con, carga)

        listaOferta = webscraping_buscojobs.scraping_ofertas(con, carga["url_principal"], carga["url_prefix"], carga["url_sufix"],
                                               carga["pagina_inicial"], carga["cant_paginas"], carga["cant_ofertas"],
                                               carga["id_carga"])
    #print(listaOferta)



if __name__ == "__main__":
    delati_portal(COMPUTRABAJO)
    #josef
    delati_buscojobs()
    delati_portal(INDEED)


   


