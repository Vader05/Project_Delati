import psycopg2


class DBWebscraping:
    def __init__(self):
        pass

    def insert_webscraping(self, connection, carga):
        mydb = connection.connect()
        try:
          #mydb = connection.connect()         
          cur = mydb.cursor() 
          # insertando un registro
          sql = "insert into webscraping (busqueda, busqueda_area, pagina_web, url_pagina, url_busqueda,fecha_creacion,fecha_modificacion, id_keyword) values (%s,%s,%s,%s,%s,current_date,current_date, %s)"
          params = (carga["busqueda"], carga["busqueda_area"], carga["pagina"], carga["url_principal"],carga["url_busqueda"],carga["id_keyword"])
          cur.execute(sql, params)                 
          mydb.commit()

          sql = "SELECT last_value FROM webscraping_id_webscraping_seq"
          cur.execute(sql)  
          id_webscraping = int(cur.fetchone()[0])
          
          # close the communication with the PostgreSQL
          cur.close()
          mydb.close()      
        except (Exception, psycopg2.DatabaseError) as error:                
            print (error)
            mydb.close()
        
        print("id webscraping: ",id_webscraping)        
        return id_webscraping


class DBOferta:
    def __init__(self):
        pass

    def insert_oferta(self, connection, oferta):        
        id_oferta=0
        mydb = connection.connect()
        try:
            #mydb = connection.connect()
            cur = mydb.cursor()                                    
            sql = "insert into Oferta (id_webscraping, titulo,empresa,lugar,salario,oferta_detalle,url_oferta,url_pagina,time_publicacion, area, id_anuncioempleo,fecha_publicacion,fecha_creacion,fecha_modificacion) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,current_date,current_date)"            
            params = (oferta["id_carga"], oferta["puesto"].strip(), oferta["empresa"].strip(), oferta["lugar"].strip(),oferta["salario"].strip(),oferta["detalle"].strip(), oferta["url"].strip(), oferta["url_pagina"].strip(), oferta["time_publicacion"].strip(), oferta["area"].strip(), oferta["id_anuncioempleo"], oferta["fecha_publicacion"])
            cur.execute(sql, params)        
            mydb.commit()            

            sql = "SELECT last_value FROM Oferta_id_Oferta_seq"
            cur.execute(sql)  
            id_oferta = int(cur.fetchone()[0])
            #print(id_oferta)  
            
            # close the communication with the PostgreSQL
            cur.close()
            mydb.close()                           

        except (Exception, psycopg2.DatabaseError) as error:                
            print ("-------------Exception, psycopg2.DatabaseError-------------------")
            print (error)
            print("insertar oferta ERROR")
            mydb.close()        
            
        return id_oferta
    
    def evitar_redundancia(self, connection, oferta):        
        mydb = connection.connect()
        try:
            #mydb = connection.connect()
            cur = mydb.cursor()                                    
            row = None
            sql = "SELECT * FROM OFERTA WHERE URL_OFERTA = '" + oferta["url"] + "' AND ID_ESTADO IS NULL LIMIT 1;" 
            #print(sql)
            cur.execute(sql)  
            row = cur.fetchone()

            # close the communication with the PostgreSQL
            cur.close()
            mydb.close()                           

        except (Exception, psycopg2.DatabaseError) as error:                
                print ("-------------Exception, psycopg2.DatabaseError-------------------")
                print (error)
                print("insertar oferta (EVITA REDUNDANCIA) ERROR")
                mydb.close()        
        return row


class DBOfertadetalle:
    def __init__(self):
        pass

    def update_ofertadetalle(self, connection, requisito):
        mydb = connection.connect()
        try:
            mycursor = mydb.cursor()
            sql = "UPDATE OFERTA_DETALLE SET descripcion_normalizada=:1 where id_ofertadetalle=:2"
            params = (requisito["descripcion_normalizada"], requisito["iddescripcion"])

            mycursor.execute(sql, params)
            mydb.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print ("-------------Exception, psycopg2.DatabaseError-------------------")
            print (error)
            print("OFERTA DETALLE UPDATE OFERTA_DETALLE ERROR")
            mydb.close()

    def insertOfertaDetalle(self, connection, listaDetalle):
        mydb = connection.connect()
        try:
            #mydb= connection.connect()
            mycursor= mydb.cursor()

            for detalle in listaDetalle:
                sql= "insert into oferta_detalle ( id_ofertadetalle, id_oferta, descripcion, fecha_creacion, fecha_modificacion) values (DEFAULT,%s,%s,current_date,current_date)"
                params= (detalle["id_oferta"],detalle["descripcion"].strip())
                mycursor.execute(sql, params)
                mydb.commit()

            # close the communication with the PostgreSQL
            mycursor.close()
            mydb.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print ("-------------Exception, psycopg2.DatabaseError-------------------")
            print (error)
            print("OFERTA DETALLE INSERTAR OFERTA_DETALLE ERROR")
            mydb.close()
        
        return 1
    def insertOfertaDetalleJOSEFF(self, connection, detalle):
        try:
            mydb= connection.connect()
            mycursor= mydb.cursor()
            sql= "insert into oferta_detalle ( id_ofertadetalle, id_oferta, descripcion, fecha_creacion, fecha_modificacion) values (DEFAULT,%s,%s,current_date,current_date)"
            params= (detalle["id_oferta"],detalle["descripcion"])
            mycursor.execute(sql, params)
            mydb.commit()
            # close the communication with the PostgreSQL
            mycursor.close()
            mydb.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print ("-------------Exception, psycopg2.DatabaseError-------------------")
            print (error)
            mydb.close()
            
        return 1
        
class DBkeyWord:
    def __init__(self):
        pass

    def getwords(self,connection):
        mydb= connection.connect()
        try:
            #mydb= connection.connect()
            mycursor= mydb.cursor()
            sql= "select id_keyword, descripcion from keyword_search"
            mycursor.execute(sql)
            palabras= list(mycursor)
            
            # close the communication with the PostgreSQL
            mycursor.close()
            mydb.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print ("-------------Exception, psycopg2.DatabaseError-------------------")
            print (error)
            print("KEYWORD ERROR")
            mydb.close()
        
        return palabras

#JOSEF
class DBKeyworSearch:
    def __init__(self):
        pass

    def obtener_descripcion(self, connection):        
        try:
            mydb = connection.connect()
            cur = mydb.cursor()                                    

            sql = "SELECT DESCRIPCION, ID_TIPOKEYWORD FROM KEYWORD_SEARCH"
            cur.execute(sql)  
            
            array_de_tuplas = []
            row = cur.fetchone()
            while row is not None:
                array_de_tuplas.append(row)
                row = cur.fetchone()

            # close the communication with the PostgreSQL
            cur.close()
            mydb.close()                           

        except (Exception, psycopg2.DatabaseError) as error:                
                print ("-------------Exception, psycopg2.DatabaseError-------------------")
                print (error)
                print("JOSEFF ERROR")
                mydb.close()        
            
        return array_de_tuplas

class DatesDB:
    def __init__(self):
        pass

    '''
    def getDate(self,connection):
        try:
            mydb= connection.connect()
            mycursor= mydb.cursor()
            sql= 'select max(o.fecha_publicacion), w.id_keyword from oferta as o inner join webscraping as w on o.id_webscraping=w.id_webscraping
                        where w.pagina_web='computrabajo' 
                    group by (w.pagina_web, w.id_keyword);'
            mycursor.execute(sql)
            tupla=list(mycursor)
            # close the communication with the PostgreSQL
            mycursor.close()
            mydb.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print ("-------------Exception, psycopg2.DatabaseError-------------------")
            print (error)
            mydb.close()
        
        return tupla
    '''

#RESETEAR FECHAS
#update oferta set fecha_publicacion=null;