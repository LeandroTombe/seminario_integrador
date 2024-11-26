from django.db import models
from datetime import datetime
import time
import xml.etree.ElementTree as ET



class Peticionesservidor(models.Model):
    peticion = models.IntegerField(db_column='PETICION', blank=True, null=True) # Field name made lowercase.
    idpetici_n = models.AutoField(db_column=u'IDPETICI\xd3N', primary_key=True) # Field name made lowercase. Field renamed to remove unsuitable characters.
    idexterna = models.CharField(db_column='IDEXTERNA', max_length=20, blank=True) # Field name made lowercase.
    estado = models.SmallIntegerField(db_column='ESTADO', blank=True, null=True) # Field name made lowercase.
    statussalida = models.TextField(db_column='STATUSSALIDA', blank=True) # Field name made lowercase.
    fecha = models.DateTimeField(db_column='FECHA', blank=True, null=True) # Field name made lowercase.
    parametro1 = models.TextField(db_column='PARAMETRO1', blank=True) # Field name made lowercase.
    parametro2 = models.TextField(db_column='PARAMETRO2', blank=True) # Field name made lowercase.
    parametro3 = models.TextField(db_column='PARAMETRO3', blank=True) # Field name made lowercase.
    instancia = models.CharField(db_column='INSTANCIA', max_length=20, blank=True) # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'PeticionesServidor'

    def set_Id(self,id):
        self.idexterna = str(str(datetime.now().strftime('%y%m%d%H%M%S%f'))[2:-4]) + str(id) + 'T'

    def add_parametro(self,campo, valor,tipo = None):
        self.parametro1 = self.parametro1 + "<" + campo + ">" + valor + "</" + campo + ">"

    def end_parametro(self):
        self.parametro1 = self.parametro1 + '</parametro1><parametro1>'

    def delete_last_end(self):
        self.parametro1 = self.parametro1[:-25]

    def ejecutar_peticion(self, tipo):
        """
        Ejecuta la petición y retorna los parametros correspondientes

        Args:
            parametro1 (tipo): numero de peticion a ejecutar.

        Returns:
            tupla de 3 valores (error,parametro2,parametro3)
        """
        self.parametro1 = '<?xml version = "1.0" encoding="Windows-1252" standalone="yes"?><VFPData><parametro1>'+self.parametro1+'</parametro1> </VFPData>'
        
        self.peticion = tipo
        self.estado = 0
        self.save(force_insert = True)
        for x in range(120):
                time.sleep(0.5)
                self = Peticionesservidor.objects.get(idexterna = self.idexterna)
                
                if self.estado > 1:
                    break
        if self.estado == 2:     
            try:
                paramXML = ET.fromstring(self.parametro2.encode('ISO-8859-1'))
                param2 = list()
                for x in paramXML:
                    nodo = dict()                    
                    for z in x:                       
                        nodo[z.tag] = z.text
                    param2.append(nodo)
                if self.parametro3:
                    paramXML3 = ET.fromstring(self.parametro3.encode('ISO-8859-1'))
                    param3 = list()
                    for i in paramXML3:
                        nodo2 = dict()                    
                        for w in i:                       
                            nodo2[w.tag] = w.text
                        param3.append(nodo2)
                else:
                    param3 = None
                return None, param2, param3                    
            except Exception as a:
                return None,None,None
        else:
            error = self.statussalida
            if not error:
                error = "Servidor de Peticiones no responde."
            return error, None,None
                        
                