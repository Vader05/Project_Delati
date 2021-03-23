
# DATABASE
DATABASE = {
    "DB_HOST" : "35.232.226.193",
    "DB_SERVICE" : "postgres",
    "DB_USER" : "postgres",
    "DB_PASSWORD" : "Oneokrock1"
}

#DATE
DATES=[
    ('enero'     , 'January'),
    ('febrero'   , 'February'),
    ('marzo'     , 'March'),
    ('abril'     , 'April'),
    ('mayo'      , 'May'),
    ('junio'     , 'June'),
    ('julio'     , 'July'),
    ('agosto'    ,'August'),
    ('septiembre', 'September'),
    ('octubre'   , 'October'),
    ('noviembre' , 'November'),
    ('diciembre' , 'December')
]

#SITIO-COMPUTRABAJO
COMPUTRABAJO = {
    "WS_PORTAL_LABORAL" : "computrabajo",
    "WS_PORTAL_LABORAL_URL" : "https://www.computrabajo.com.pe/",
    "WS_PAGINAS" : 20,  # 500 CANTIDAD DE PAGINAS A SCRAPEAR
    "WS_PAGINA_INICIAL" : 1,  # NUMERO DE PAGINA DESDE DONDE SE EMPEZARA A SCRAPEAR
    "WS_OFERTAS" : None,  # CANTIDAD DE OFERTAS POR PAGINA A SCRAPEAR (None: Sin limite)
    "WS_AREA" : None,  # FILTRO DE AREA PARA REALIZAR LA BUSQUEDA (None: Sin filtro)
    "PAGINADO":"&p="
}

#SITIO-INDEED
INDEED= {
    "WS_PORTAL_LABORAL" : "indeed",
    "WS_PORTAL_LABORAL_URL" : "https://pe.indeed.com",
    "WS_PAGINAS" : 20,  # 500 CANTIDAD DE PAGINAS A SCRAPEAR
    "WS_PAGINA_INICIAL" : 1,  # NUMERO DE PAGINA DESDE DONDE SE EMPEZARA A SCRAPEAR
    "WS_OFERTAS" : None,  # CANTIDAD DE OFERTAS POR PAGINA A SCRAPEAR (None: Sin limite)
    "WS_AREA" : None,  # FILTRO DE AREA PARA REALIZAR LA BUSQUEDA (None: Sin filtro)
    "PAGINADO" :"&start="
}

#SITIO-BUSCOJOBS
BUSCOJOBS= {
    "WS_PORTAL_LABORAL" : "buscojobs",
    "WS_PORTAL_LABORAL_URL" : "https://www.buscojobs.pe",
    "WS_PAGINAS" : 2,  # 500 CANTIDAD DE PAGINAS A SCRAPEAR
    "WS_PAGINA_INICIAL" : 1,  # NUMERO DE PAGINA DESDE DONDE SE EMPEZARA A SCRAPEAR
    "WS_OFERTAS" : None,  # CANTIDAD DE OFERTAS POR PAGINA A SCRAPEAR (None: Sin limite)
    "WS_AREA" : None,  # FILTRO DE AREA PARA REALIZAR LA BUSQUEDA (None: Sin filtro)
    "NAME_TEAM": 'JJERK'
}