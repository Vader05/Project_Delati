from urllib.request import urlopen
from urllib.error import HTTPError
import bs4
from bs4 import BeautifulSoup
import requests
from controller import Controller
from configuration import INDEED
import datetime
from timeit import default_timer

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
    fecha_publicacion=fecha_publicacion.strip().replace(u'\xa0', u' ')
    array_fecha_publicacion=fecha_publicacion.split(" ")
    if fecha_publicacion=="Recién publicado" or fecha_publicacion=="Hoy":
        fecha_aviso=fecha_actual.date()
    else:
        fecha_numero=int(array_fecha_publicacion[-2])
        fecha_aviso=fecha_actual.date()+datetime.timedelta(days=-fecha_numero)
    
    return fecha_aviso

def scraping_ofertas(con, url_principal, prefix_url, sufix_url, pagina_inicial, cant_paginas, cant_ofertas, id_carga):
    controller = Controller()
    lista_oferta = []       
    i=1
    
    #HALLAMOS LA FECHA ACTUAL
    fecha_actual=datetime.datetime.now() 

    #for i in range(pagina_inicial, cant_paginas):
    for i in range(INDEED["WS_PAGINA_INICIAL"], INDEED["WS_PAGINAS"]):
        print("\033[0;32m"+'NUMERO DE PÁGINA: '+ str(i))
        url_pagina = prefix_url + str(i*10)

        req = requests.get(url_pagina)
        soup = BeautifulSoup(req.text, "lxml")
        #avisos = soup.find_all("div", {"class": "aviso-simple"})
        avisos=soup.findAll("table")[4].find("td", {"id": "resultsCol"}).findAll("div", {"class": "jobsearch-SerpJobCard"})                        
     
        lista_oferta = []
        for el in avisos:

            oferta = {}
            lista_tupla=[]
            lista_final=[]    

            # Obtiene el link para poder ver el detalle de la oferta
            href = el.find("a")['href']
            link = url_principal + href

            oferta["id_carga"] = id_carga
            # Almacena la url de la pagina
            oferta["url_pagina"] = url_pagina
            # Almacena la url de la oferta
            oferta["url"] = link

            #VEMOS SI LA PUBLICACION SE REPITE
            redundancia  = controller.evitar_redundancia(con, oferta)
            if redundancia is None :
                print("---------------------------------")
                print("\033[0;34m"+'REGISTRANDO ANUNCIO A LA BD')

                oferta["puesto"]  =el.find("h2", {"class": "title"}).get_text()
                print("PUESTO DEL AVISO: ",oferta["puesto"] )

                empresa= el.find("span", {"class": "company"})  
                if empresa!=None:                            
                    oferta["empresa"]=empresa.get_text()
                else:
                    oferta["empresa"]='No especificado'
                print("EMPRESA: ", oferta["empresa"].strip() )


                lugar   = el.find("span", {"class": "location"})
                if lugar!=None:                                            
                    oferta["lugar"]=lugar.get_text()
                else:
                    oferta["lugar"]=''                
                
                print("UBICACION: ",oferta["lugar"] )

                salario = el.find("span", {"class": "salaryText"})            
                if salario!=None:                                            
                    oferta["salario"]=salario.get_text()
                else:
                    oferta["salario"]='No especificado' 

                print("SALARIO: ", oferta["salario"])

                
                #OBTENEMOS LA FECHA DE AVISO
                fecha_publicacion=el.find("span",{"class":"date"}).get_text()
                oferta["time_publicacion"]=fecha_publicacion
                print("FECHA: ", oferta["time_publicacion"])
                fecha_aviso=get_fecha_publicacion(fecha_actual, fecha_publicacion)
                if fecha_aviso!=None:
                    oferta["fecha_publicacion"]=fecha_aviso
                else:
                    oferta["fecha_publicacion"]='No especificado'   
                print("FECHA DEL AVISO: ",oferta["fecha_publicacion"] )


                #OBTENEMOS EL ID DEL TRABAJO
                id_anuncioempleo=el["data-jk"]
                oferta["id_anuncioempleo"] = id_anuncioempleo
                print("ID DEL ANUNCION: ", oferta["id_anuncioempleo"])


                #OBTENEMOS EL AREA (EN INDEED NO EXISTE ASI QUE LO INICIALIZAMOS [])
                oferta["area"]='No especificado'

                # Accede al contenido HTML del detalle de la oferta
                reqDeta = requests.get(oferta["url"])            
                soup_deta = BeautifulSoup(reqDeta.text, "lxml")

                #aviso_deta = soup_deta.find("div", {"id": "vjs-desc"})
                aviso_deta = soup_deta.find("div", {"id": "jobDescriptionText"})
                if aviso_deta!=None:                                            
                    oferta["detalle"]=aviso_deta.get_text()

                lista_oferta.append(oferta)            

                row = controller.registrar_oferta(con, oferta)
                print("ID DE OFERTA: ", row)

                inicio=default_timer()
                #aviso_tupla = soup_deta.find("div", {"id": "jobDescriptionText"}).findChildren()
                aviso_tupla = soup_deta.find("div", {"id": "jobDescriptionText"})
                for av_linea in aviso_tupla.stripped_strings:
                    lista_tupla.append(av_linea.strip())

                for descripcion in lista_tupla:
                    a={}
                    a["id_oferta"]=row
                    a["descripcion"]=descripcion
                    lista_final.append(a)

                controller.registrar_detalle_oferta(con, lista_final)
                fin=default_timer()
                print("DURACION: ", str(fin-inicio)) 
            else: 
                print("\033[0;31m"+'NO REGISTRAR A LA BD')
                print("--------------------------")
                  
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
