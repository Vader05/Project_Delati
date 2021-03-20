# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib.error import HTTPError
import bs4
from bs4 import BeautifulSoup
import requests
from controller import Controller
from configuration import BUSCOJOBS
import unicodedata

from datetime import date
from datetime import datetime
from datetime import timedelta

def contain_br(contents):
    for element in contents:
        if type(element) is bs4.element.Tag:
            if element.name == "br":
                return True
    return False


def get_content(contents):
    lista = []
    for element in contents:
        if type(element) is bs4.element.NavigableString:
            if str(element) is not None and str(element).strip() != "":
                lista.append(str(element))
    return lista


def scraping_ofertas(con, url_principal, prefix_url, sufix_url, pagina_inicial, cant_paginas, cant_ofertas, id_carga):
    controller = Controller()
    lista_oferta = []       
    i=1
    m=0  

    obtener_lista_keywords(con)

    #for i in range(pagina_inicial, cant_paginas):
    for i in range(BUSCOJOBS["WS_PAGINA_INICIAL"], BUSCOJOBS["WS_PAGINAS"]+1):
        #print(prefix_url)
        url_pagina = prefix_url + str(i)
        #print("------------------for i in range(pagina_inicial, cant_paginas)-------------------")
        print(url_pagina)

        req = requests.get(url_pagina)
        soup = BeautifulSoup(req.text, "lxml")
        try:
            avisos=soup.findAll("div", attrs={"class":"row result click"})                            
        except:
            avisos=[]

        lista_oferta = []
        for el in avisos:
            
            oferta = {}    


            href = el.find("a")['href'][2:]
            link = "http://" + href
            
            oferta["id_carga"] = id_carga
            # Almacena la url de la pagina
            oferta["url_pagina"] = url_pagina
            # Almacena la url de la oferta
            oferta["url"] = link
            #print(oferta["url"].split("-")[-1])

            redundancia  = controller.evitar_redundancia(con, oferta)
            #redundancia = None
            if(redundancia is None):
                print("Registro nuevo")

                oferta["time_publicacion"] = elimina_tildes(el.find("span", attrs={"class": "pull-right"}).get_text().strip())
                #print(oferta["time_publicacion"])

                fecha_p = oferta["time_publicacion"].split(" ")
                oferta["fecha_publicacion"] = fecha_publicacion(fecha_p[-1], fecha_p[-2])
                #print(oferta["fecha_publicacion"])
            
                oferta["puesto"] = elimina_tildes(el.find("h3", {"class": ""}).get_text().strip()[0:200])

                try:
                    oferta["lugar"] = elimina_tildes(el.find("span", attrs={"class": ""}).get_text().strip().split("-")[1].strip())
                except:
                    oferta["lugar"] = elimina_tildes(el.find("span", attrs={"class": ""}).get_text().strip().split("-")[0].strip())
                
                # Accede al contenido HTML del detalle de la oferta
                reqDeta = requests.get(oferta["url"])            
                soup_deta = BeautifulSoup(reqDeta.text, "lxml")

                oferta_d=soup_deta.find("div", attrs={"class":"oferta-main-top"})                    
                try:
                    oferta["empresa"] = elimina_tildes(oferta_d.find("h2", attrs={"class":""}).get_text().strip())
                except:
                    oferta["empresa"] = "NO ESPECIFICADO"

                oferta["salario"] = "NO ESPECIFICADO"


                try: 
                    oferta["area"]=elimina_tildes(oferta_d.findAll("a", attrs={"class": ""})[-1].get_text().strip())
                except:
                    oferta["area"] = "NO ESPECIFICADO"
                
                oferta["id_anuncioempleo"] = link.split('-')[-1]

                try:
                    paga = soup_deta.findAll("div", attrs={"class": "row oferta-contenido"})
                    str3 = paga[0].get_text().splitlines()
                    str3 = list(filter(None, str3))
                    if(str3[2][0] == 'S'):
                        oferta["salario"] = elimina_tildes(str3[2].split(":")[-1].strip())
                except:
                    print("except")
                
                aviso_deta = soup_deta.find("div", attrs={"class":"col-md-12 descripcion-texto"})
                if aviso_deta!=None:                                            
                    oferta["detalle"]=elimina_tildes(aviso_deta.get_text().strip()[0:800])
                else:
                    oferta["detalle"] = ""
                lista_oferta.append(oferta)  
                row_id = controller.registrar_oferta(con, oferta)
                scraping_ofertadetalle(link, row_id, con)
            else:
                print("Registro redundante")

    return lista_oferta


def scraping_ofertadetalle(url_pagina, row_id, con):
    controller = Controller()
    detalle = {}
    detalle["id_oferta"] = row_id
    print(detalle["id_oferta"])
    req = requests.get(url_pagina)
    soup = BeautifulSoup(req.text, "lxml")
    
    contenido = soup.find("div", attrs={"class": "col-md-12 descripcion-texto"})
    try: 
        str_list = elimina_tildes(contenido.decode_contents().replace("</p>", '').replace("<p>", '').replace("-", '').replace("•", '').strip()).split('<BR/>')
    except: 
        str_list = []
        
    str_list = list(filter(None, str_list))

    #print(str_list)
    """
    try:
        contenido_extra = soup.findAll("div", attrs={"class": "row oferta-contenido"})
        str_list2 = elimina_tildes(contenido_extra[-1].get_text().replace("•", '')).splitlines()
        str_list2 = list(filter(None, str_list2))
    except:
        str_list2 = []
    """
    #print(str_list2)



    for s_contenido in str_list:
        detalle["descripcion"] = s_contenido.strip()[0:2000]
        controller.registrar_oferta_detalle(con, detalle)
    
    """
    for s_contenido_x in str_list2:
        detalle["descripcion"] = s_contenido_x.strip()
        controller.registrar_oferta_detalle(con, detalle)
    """
    return 1


def replace_quote(list):
    new_list = []
    for el in list:
        el = el.replace("'", "''")
        new_list.append(el)
    return new_list


def obtener_lista_keywords(con):
    controller = Controller()
    lista_busquedas = []
    i = 1
    for search in controller.obtener_keyword_search(con): 
        busqueda = {}
        if search != None:
            busqueda["descripcion"] = '/search/' + search[0].replace(" ", "-").replace(".", "")
            busqueda["id"] = i
            lista_busquedas.append(busqueda)
            i += 1

    return lista_busquedas


def elimina_tildes(cadena):
    s = ''.join((c for c in unicodedata.normalize('NFD',cadena) if unicodedata.category(c) != 'Mn'))
    return s.upper()

def fecha_publicacion(modalidad, tiempo):
    if(tiempo == "UN"):
        tiempo = 1

    tiempo = int(tiempo)
    switcher = {
        "HORAS": datetime.now() + timedelta(days=-tiempo/24),       
        "DIA":   datetime.now() + timedelta(days=-1),
        "DIAS":  datetime.now() + timedelta(days=-tiempo),
        "MES":   datetime.now() + timedelta(days=-30),
        "MESES": datetime.now() + timedelta(days=-tiempo*30)
    }
    return switcher.get(modalidad,datetime.now())