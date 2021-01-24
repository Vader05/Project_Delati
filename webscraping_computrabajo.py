from urllib.request import urlopen
from urllib.error import HTTPError
import bs4
from bs4 import BeautifulSoup
import requests
from controller import Controller
from configuration import COMPUTRABAJO, DATES
import datetime


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


def get_fecha_publicacion(fecha_actual, fecha_publicacion):
    #MODIFICANDO AÑADIR FECHA DE PUBLICACION 
    fecha_aviso=fecha_actual.date()
    #fecha_actual=datetime.datetime.now() 
    #fecha_publicacion=el.find("span",{"class":"dO"}).get_text()
    #print('FECHA HOY:',fecha_actual)
    #print('FECHA PUBLICACION',fecha_publicacion)
    array_fecha_publicacion=fecha_publicacion.split(" ")
    if array_fecha_publicacion[0].strip()=="Ayer,":
        fecha_aviso=fecha_actual.date()+datetime.timedelta(days=-1)
        #print('FECHA PUBLICACION AVISO:', fecha_aviso)
    else:
        if array_fecha_publicacion[0].strip()!="Hoy,":
            for date in DATES:
                if(date[0]==array_fecha_publicacion[1]):
                    array_fecha_publicacion[1]=date[1]
            #Obtengo fecha de publicación
            fecha_aviso = datetime.datetime.strptime(str(array_fecha_publicacion[0]+' '+array_fecha_publicacion[1]), '%d %B')
            #OBTENGO MES DE LA PUBLICACION
            fecha_aviso_mes=fecha_aviso.month
            #OBTENGO MES DE LA FECHA DE HOY
            fecha_actual_mes=fecha_actual.month
            #COMPARO MESES
            #SI EL MES DE LA PUBLICACION ES MAYOR AL MES ACTUAL, ES DEL AÑO PASADO
            if(fecha_aviso_mes>fecha_actual_mes):
                array_fecha_publicacion.append((fecha_actual.date()-datetime.timedelta(days=365)).year)
                fecha_aviso = datetime.datetime.strptime(str(array_fecha_publicacion[0]+' '+array_fecha_publicacion[1]+' '+str(array_fecha_publicacion[2])), '%d %B %Y')
            # print('FECHA PUBLICACION AVISO:', fecha_aviso.date())
            #SINO ES DEL AÑO ACTUAL
            else:
                array_fecha_publicacion.append(fecha_actual.year)
                fecha_aviso = datetime.datetime.strptime(str(array_fecha_publicacion[0]+' '+array_fecha_publicacion[1]+' '+str(array_fecha_publicacion[2])), '%d %B %Y')
                #print('FECHA PUBLICACION AVISO:', fecha_aviso.date())
            fecha_aviso=fecha_aviso.date()
        else:
            print('El anuncio es de hoy')
    return fecha_aviso

def scraping_ofertas(con, url_principal, prefix_url, sufix_url, pagina_inicial, cant_paginas, cant_ofertas, id_carga, fecha_max_publicacion):
    controller = Controller()
    lista_oferta = []       
    i=1
    #HALLAMOS LA FECHA ACTUAL

    fecha_actual=datetime.datetime.now() 

    #for i in range(pagina_inicial, cant_paginas):
    for i in range(COMPUTRABAJO["WS_PAGINA_INICIAL"], COMPUTRABAJO["WS_PAGINAS"]):
        print("\033[0;32m"+'NUMERO DE PÁGINA: '+ str(i))

        #print(prefix_url)

        #MODIFICADO-----------------------------
        url_pagina = prefix_url + str(i)
        #print("------------------for i in range(pagina_inicial, cant_paginas)-------------------")
        #print(i)

        req = requests.get(url_pagina)
        soup = BeautifulSoup(req.text, "lxml")
        #avisos = soup.find_all("div", {"class": "aviso-simple"})
        
        
        #avisos=soup.findAll("table")[4].find("td", {"id": "resultsCol"}).findAll("div", {"class": "jobsearch-SerpJobCard"})                        
        avisos=soup.findAll("section")[0].find("div",{"class": "gO"}).findAll("div", {"class": "bRS"})                      
        
        
        
        #print("----------------------")
        #print(avisos)
        #cont = 0        
        lista_oferta = []
        for el in avisos:
            #MODIFICADO
            el=el.find("div",{"class", "iO"})

            #MODIFICADO PARA FECHAS 22/01/2021
            
            #Class de fecha de publicacion del anuncio
            fecha_publicacion=el.find("span",{"class":"dO"}).get_text()
            #OBTENEMOS LA FECHA DE AVISO
            fecha_aviso=get_fecha_publicacion(fecha_actual, fecha_publicacion)
            #COMPARAMOS FECHAS
            print('FECHA AVISO:', fecha_aviso)
            print('FECHA MAYOR:', fecha_max_publicacion)
            if fecha_aviso>fecha_max_publicacion:
                print("\033[0;34m"+'REGISTRANDO ANUNCIO A LA BD')

                #print("-------avisos--------")
                #print(len(avisos))
                oferta = {}
                
                oferta["fecha_publicacion"]=fecha_aviso
                #cont = cont + 1
                #if cant_ofertas is not None:
                #    if cont > cant_ofertas:
                #        break
                # Obtiene el link para poder ver el detalle de la oferta
                href = el.find("a")['href']
                link = url_principal + href

                oferta["id_carga"] = id_carga
                # Almacena la url de la pagina
                oferta["url_pagina"] = url_pagina
                # Almacena la url de la oferta
                oferta["url"] = link

                #MODIFICADO

                #oferta["puesto"]  =el.find("h2", {"class": "title"}).get_text()
                oferta["puesto"]  =el.find("h2", {"class": "tO"}).get_text()
                
                
                # empresa= el.find("span", {"class": "company"}) 
                empresa= el.find("span", {"itemprop": "name"})
                if empresa!=None:                            
                    oferta["empresa"]=empresa.get_text()
                else:
                    oferta["empresa"]=''
                
                # lugar   = el.find("span", {"class": "location"})
                lugar   = el.find("span", {"itemprop": "addressLocality"})
                region  = el.find("span", {"itemprop": "addressRegion"})
                if lugar!=None:                                            
                    oferta["lugar"]=lugar.get_text() + " - " + region.get_text()
                else:
                    oferta["lugar"]=''                
                    
                #print("--------------------------------")

                #MODIFICANDO

                # Accede al contenido HTML del detalle de la oferta
                reqDeta = requests.get(oferta["url"])            
                soup_deta = BeautifulSoup(reqDeta.text, "lxml")


                #aviso_deta = soup_deta.find("div", {"id": "vjs-desc"})
                aviso_deta = soup_deta.find("div", {"class": "bWord"})
                if aviso_deta!=None:                                            
                    oferta["detalle"]=aviso_deta.get_text()


                #salario = el.find("span", {"class": "salaryText"})  
                # salario= soup_deta.findAll("section")[4]
                # print(salario)         
                salario = soup_deta.findAll("section")[4].find("ul").findAll("li")[5].find("p")            
                if salario!=None:                                            
                    oferta["salario"]=salario.get_text()
                else:
                    oferta["salario"]='' 

                # # Accede al contenido HTML del detalle de la oferta
                # reqDeta = requests.get(oferta["url"])            
                # soup_deta = BeautifulSoup(reqDeta.text, "lxml")

                # #aviso_deta = soup_deta.find("div", {"id": "vjs-desc"})
                # aviso_deta = soup_deta.find("div", {"id": "jobDescriptionText"})
                # if aviso_deta!=None:                                            
                #     oferta["detalle"]=aviso_deta.get_text()

                lista_oferta.append(oferta)            

                row = controller.registrar_oferta(con, oferta)
                print("id de la oferta: ",row)

                tuplas=[]
                aviso_tupla = soup_deta.find("div", {"class": "bWord"}).find("ul")
                if aviso_tupla!=None:
                    i=0                                            
                    aviso_detalle_tupla= soup_deta.find("div", {"class": "bWord"}).find("ul").findChildren()
                    for aviso in aviso_detalle_tupla:
                        detalle={}

                        if aviso.get_text().strip():
                            
                            if i==2:
                                #print("-------------analisando li2------------------")
                                #print(aviso.get_text())
                                tuplaLista=controller.analizaSegundoLi(aviso, row)
                                #print(tuplaLista)
                                controller.registrar_detalle_oferta(con, tuplaLista)

                            else:
                                detalle["id_oferta"]=row
                                detalle["descripcion"]=aviso.get_text().strip()
                                tuplas.append(detalle)
                                #print(aviso.get_text())
                                #print("-----------------------------")
                    
                        i=i+1
                    #print("fin de tupla")
                    #print(tuplas)
                    controller.registrar_detalle_oferta(con, tuplas)
                    
                #print("fin de aviso")
            else: 
                print("\033[0;31m"+'NO REGISTRAR A LA BD')
                return None
    
    return lista_oferta


def scraping_ofertadetalle(url_pagina, link, id_carga):
    oferta = {}
    # Almacena la url de la pagina
    oferta["url_pagina"] = url_pagina
    # Almacena la url de la oferta
    oferta["url"] = link
    # Accede al contenido HTML de la cabecera de la oferta
    reqCab = requests.get(oferta["url_pagina"])
    soup_cab = BeautifulSoup(reqCab.text, "lxml")
    oferta["puesto"]  =soup_cab.find("div", {"class": "jobsearch-SerpJobCard"}).find("h2", {"class": "title"}).get_text()
    empresa = soup_cab.find("div", {"class": "jobsearch-SerpJobCard"}).find_all("span", {"class": "company"})
    print(len(empresa))
    oferta["empresa"]=empresa[0].get_text()

    oferta["lugar"]   = soup_cab.find("div", {"class": "jobsearch-SerpJobCard"}).find("span", {"class": "location accessible-contrast-color-location"})
    oferta["salario"] = soup_cab.find("div", {"class": "jobsearch-SerpJobCard"}).find("span", {"class": "salaryText"})

    #title=bsObj.find_all("div", {"class": "summary"})


    # Accede al contenido HTML del detalle de la oferta
    reqDeta = requests.get(oferta["url"])
    #print(oferta["url"])
    soup_deta = BeautifulSoup(reqDeta.text, "lxml")
    # Obtiene el nombre del puesto de trabajo
    #oferta["puesto"] = soup_deta.find("div", {"id": "vjs-jobtitle"})
    # Obtiene el nombre de la empresa
    #oferta["empresa"] = soup_deta.find("span", {"id": "vjs-cn"})
    #oferta["lugar"] = soup_deta.find("span", {"id": "vjs-loc"})
    #oferta["salario"] = soup_deta.find("div", {})
    # Obtiene los div z-group en el cual esta contenido los datos resumen de la oferta, tales como:
    # Lugar, Tiempo de Publicacion, Salario, Tipo de Puesto, Area
    #aviso_deta = soup_deta.find("div", {"id": "vjs-desc"})
    #aviso_deta1= aviso_deta
    #for ed in aviso_deta:
        # Obtiene el titulo del dato resumen
        #cabecera_deta = ed.find("div", {"class": "spec_attr"})
        # Obtiene el contenido del dato resumen
        #children_descripcion_deta = ed.find("div", {"class": "spec_def"}).findChildren()
        #descripcion_deta = children_descripcion_deta[len(children_descripcion_deta) - 1].text.strip()
        #if cabecera_deta.find("h2", {"class": "lugar"}) is not None:
        #    oferta["lugar"] = descripcion_deta
        #elif cabecera_deta.find("h2", {"class": "fecha"}) is not None:
        #    oferta["tiempoPublicado"] = descripcion_deta
        #elif cabecera_deta.find("h2", {"class": "salario"}) is not None:
        #    oferta["salario"] = descripcion_deta
        #elif cabecera_deta.find("h2", {"class": "tipo_puesto"}) is not None:
        #    oferta["tipoPuesto"] = descripcion_deta
        #elif cabecera_deta.find("h2", {"class": "area"}) is not None:
        #    oferta["area"] = descripcion_deta
    #oferta["prop_area"] = soup_deta.find('input', {'id': 'area'}).get("value")
    #oferta["prop_subarea"] = soup_deta.find('input', {'id': 'subarea'}).get("value")
    # Obtiene la descripcion de la Oferta(Requisitos)
    # Almacena lo contenido en etiquetas <p> y <li>
    # Extrae informacion de etiquetas <p>
    #aviso_descripcion = soup_deta.find("div", {"class": "aviso_description"})
    #descripcion_deta_p = aviso_descripcion.find_all("p")
    #lista_detalle = []
    #for ed in descripcion_deta_p:
    #    content = ed.contents
    #    if content is not None and contain_br(content):
    #        lista_detalle.extend(get_content(content))
    #    else:
    #        if ed.text is not None and ed.text.strip() != "":
    #            lista_detalle.append(ed.text)

    # Extrae informacion de etiquetas <li>
    #descripcion_deta_ul = aviso_descripcion.find_all("ul")
    #for ed in descripcion_deta_ul:
    #    descripcion_deta_ul_li = ed.find_all("li")
    #    for edc in descripcion_deta_ul_li:
    #        children = edc.findChildren()
    #        descripcion = {}
    #        if len(children) > 0:
    #            text = children[len(children) - 1].text.strip()
    #            descripcion["descripcion"] = text
    #            if text is not None and text.strip() != "":
    #                lista_detalle.append(text)
    #       else:
    #            text = edc.text
    #            descripcion["descripcion"] = text
    #            if text is not None and text.strip() != "":
    #                lista_detalle.append(text)
    #lista_detalle.append(aviso_deta.get_text())                    
    #lista_detalle=aviso_deta.get_text()
    #oferta["listaDescripcion"] = replace_quote(lista_detalle)
    #oferta["listaDescripcion"] = aviso_deta1
    oferta["id_carga"] = id_carga

    print(oferta)
    return oferta


def replace_quote(list):
    new_list = []
    for el in list:
        el = el.replace("'", "''")
        new_list.append(el)
    return new_list
