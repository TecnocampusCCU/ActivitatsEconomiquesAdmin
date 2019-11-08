# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ActivitatsEconomiquesAdmin
                                 A QGIS plugin
 ActivitatsEconomiquesAdmin
                              -------------------
        begin                : 2018-05-24
        git sha              : $Format:%H$
        copyright            : (C) 2018 by ccu
        email                : jlopez@tecnocampus.cat
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import sys
import os
from os.path import expanduser
from PyQt4 import QtGui,QtCore
from PyQt4.QtCore import * #QSettings, QTranslator, qVersion, QCoreApplication
#from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import * #QAction, QIcon,QColor
from qgis.core import QgsMapLayer
from qgis.core import QgsDataSourceURI
from qgis.core import QgsVectorLayer
from qgis.core import QgsVectorFileWriter
from qgis.core import QgsGraduatedSymbolRendererV2
from qgis.core import QgsVectorGradientColorRampV2
from qgis.core import QgsMapLayerRegistry
from qgis.core import QgsRendererRangeV2
from qgis.core import QgsSymbolV2
from qgis.core import QgsFillSymbolV2
from qgis.core import QgsRandomColorsV2
from qgis.core import QgsRendererRangeV2LabelFormat
from qgis.core import QgsProject
from qgis.core import QgsMessageLog
from qgis.core import QgsLayerTreeLayer
from qgis.core import QGis
from PyQt4.QtGui import QProgressBar
from qgis.gui import QgsMessageBar
from qgis.utils import iface
from qgis.analysis import QgsGeometryAnalyzer
from PyQt4.QtSql import *
from PyQt4.QtCore import *
from datetime import date, datetime
import datetime
import time
import qgis
#from PyQt4.QtGui import QMessageBox
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from ActivitatsEconomiquesAdmin_dialog import ActivitatsEconomiquesAdminDialog
import os.path
import psycopg2
from email.header import UTF8
#from test.test_uu import plaintext
nomBD1=""
contra1=""
host1=""
port1=""
usuari1=""
schema=""
cur=None
conn=None
micolor_Topo=None
micolor_ZI=None
micolor_Graf=None
Fitxer=""
Path_Inicial=expanduser("~")
Versio_modul="V_18.0524"
progress=None
Auto_generacio=False
path_file=""
ArxiuTrobat=False
Auto_primera_vegada=True
mes = {1:"Gener", 2:"Febrer", 3:"Març", 4:"Abril", 5:"Maig", 6:"Juny", 7:"Juliol", 8:"Agost", 9:"Setembre", 10:"Octubre", 11:"Novembre", 12:"Desembre"}

class ActivitatsEconomiquesAdmin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ActivitatsEconomiquesAdmin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ActivitatsEconomiquesAdminDialog()
        self.dlg.btn_cerca.clicked.connect(self.on_click_cerca)
        self.dlg.btn_totes.clicked.connect(self.on_click_totes)
        self.dlg.btn_esborra_sel_Nom.clicked.connect(self.on_click_Borra_seleccio_noms)
        self.dlg.btn_esborra_sel_Numero.clicked.connect(self.on_click_Borra_seleccio_numeros)
        self.dlg.ListaActivitatsEpigraf.selectionModel().selectionChanged.connect(self.on_seleccion_change_Epigrafs)
        self.dlg.ListaActivitatsDesc.selectionModel().selectionChanged.connect(self.on_seleccion_change_Desc)
        self.dlg.btn_mostra_sel.clicked.connect(self.on_click_mostra_seleccio)
        self.dlg.ListaActivitatsDesc.clicked.connect(self.on_click_List)
        #self.dlg.ListaActivitatsEpigraf.clicked.connect(self.on_click_ListEpigraf)
        self.dlg.INICI.clicked.connect(self.on_click_INICI)
        self.dlg.Sortir.clicked.connect(self.on_click_Sortir)
        self.dlg.AutoGenera.clicked.connect(self.on_click_AutoGenera)
        
        self.dlg.ComboConn.currentIndexChanged.connect(self.on_Change_ComboConn)
        self.dlg.GrafCombo.currentIndexChanged.connect(self.on_Change_GrafCombo)
        self.dlg.ColorTopos.clicked.connect(self.on_click_ColorTopos)
        self.dlg.ColorZI.clicked.connect(self.on_click_ColorZI)
        self.dlg.ColorGraf.clicked.connect(self.on_click_ColorGraf)
        self.dlg.Veure_ZI.stateChanged.connect(self.on_click_Veure_ZI)
        self.dlg.ZIGraf_radio.toggled.connect(self.on_toggled_ZIGraf_radio)
        self.dlg.parcela.toggled.connect(self.on_toggled_parcela)
        self.dlg.Transparencia.valueChanged.connect(self.on_valuechange_Transparencia)
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&CCU')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'CCU')
        self.toolbar.setObjectName(u'ActivitatsEconomiquesAdmin')

        self.bar = QgsMessageBar()
        self.bar.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )
        self.dlg.setLayout(QGridLayout())
        self.dlg.layout().setContentsMargins(0, 0, 0, 0)
        self.dlg.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.dlg.buttonbox.accepted.connect(self.run)
        self.dlg.buttonbox.setVisible(False)
        self.dlg.layout().addWidget(self.dlg.buttonbox, 0, 0, 2, 1)
        self.dlg.layout().addWidget(self.bar, 0, 0,1,1)
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ActivitatsEconomiquesAdmin', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ActivitatsEconomiquesAdmin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'ActivitatsEconomiquesAdmin'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def EstatInicial(self):
        """Aquesta funcio reseteja l'estat de tots els elements de la interficie"""
        global Versio_modul
        self.bar.clearWidgets()
        self.dlg.versio.setText(Versio_modul)
        self.dlg.ColorTopos.setStyleSheet('border:1px solid #000000; background-color: #ff0000')
        self.dlg.ColorTopos.setAutoFillBackground(True)
        self.dlg.ColorZI.setStyleSheet('border:1px solid #000000; background-color: #aaffff')
        self.dlg.ColorZI.setAutoFillBackground(True)
        self.dlg.AutoGen.setVisible(True)
        #self.dlg.VeureZI_panel.setStyleSheet('border:0px')
        self.dlg.VeureZI_panel.setVisible(False)
        self.dlg.barraCerca.clear()
        self.dlg.barraCerca.setStyleSheet("font-size: 14px; border: 1px #000000; background-color: #FFFFFF")
        self.dlg.ZIGraf_panel.setVisible(False)
        self.dlg.Poblacio_panel.setVisible(False)
        self.dlg.ListaActivitatsDesc.clear()
        self.dlg.ListaActivitatsEpigraf.clear()
        self.dlg.ListaActivitatsEpigraf.setVisible(True)
        #self.dlg.SSTab2.removeTab(1)
        self.dlg.texte_2.setText(u'1')
        self.dlg.texte_3.setText(u"Llista d'Epígrafs")
        self.dlg.EstatConnexio.setText(u'No connectat')
        self.dlg.parcela.setChecked(False)
        self.dlg.parcela.setChecked(True)
        self.dlg.Radi_ZI.setText(u'150')
        self.dlg.Veure_ZI.setChecked(False)
        self.dlg.ColorTopos.setStyleSheet('border:1px solid #000000; background-color: #ff0000')
        self.dlg.ColorZI.setStyleSheet('border:1px solid #000000; background-color: #aaffff')
        self.dlg.ColorGraf.setStyleSheet('border:1px solid #000000; background-color: #ff0000')
        self.dlg.EstatConnexio.setStyleSheet('border:1px solid #000000; background-color: #FFFFFF')
        self.dlg.SSTab1.setCurrentIndex(0)
        self.dlg.SSTab2.setCurrentIndex(0)
        self.dlg.RelacionarPoblacio.setChecked(False)
        self.dlg.NoMostrarZI.setChecked(False)
        self.dlg.ColorDegradat.setCurrentIndex(0)
        self.dlg.Transparencia.setValue(50)
        self.dlg.ZICirc_radio.setChecked(False)
        self.dlg.ZICirc_radio.setChecked(True)
        self.dlg.ZIGraf_radio.setVisible(True)
        self.dlg.CostNusos.setVisible(True)
        self.dlg.GrafCombo.setCurrentIndex(0)
        self.dlg.CostInvers_chk.setVisible(False)
        self.dlg.CalculRadiTopos_panel.setVisible(False)
        self.dlg.buf_chk.setVisible(False)
        #progress.setValue(0)
        self.dlg.Progres.setValue(0)
        self.dlg.Progres.setVisible(False)
        self.dlg.btn_mostra_sel.setVisible(False)
        self.dlg.Mostra_punt_chk.setChecked(True)

        qApp.processEvents()
        
        #self.dlg.EstatConnexio.setStyleSheet('border:1px solid #000000; background-color: #ffff7f')
        self.dlg.Transparencia_lbl.setText(str(self.dlg.Transparencia.value())+u' %')

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ActivitatsEconomiquesAdmin'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def populateComboBox(self,combo,list,predef,sort):
        """Aquesta funcio omple les pestanyes desplegables amb els paramtres que li passem per parametres"""
        #procedure to fill specified combobox with provided list
        combo.blockSignals (True)
        combo.clear()
        model=QStandardItemModel(combo)
        predefInList = None
        for elem in list:
            try:
                item = QStandardItem(unicode(elem))
            except TypeError:
                item = QStandardItem(str(elem))
            model.appendRow(item)
            if elem == predef:
                predefInList = elem
        if sort:
            model.sort(0)
        combo.setModel(model)
        if predef != "":
            if predefInList:
                combo.setCurrentIndex(combo.findText(predefInList))
            else:
                combo.insertItem(0,predef)
                combo.setCurrentIndex(0)
        combo.blockSignals (False)

    def getConnections(self):
        """Aquesta funcio obte les connexions del nostre projecte QGIS"""
        s = QSettings() 
        s.beginGroup("PostgreSQL/connections")
        currentConnections = s.childGroups()
        #print "connections: ",currentConnections
        s.endGroup()
        return currentConnections

    def getGeometryType(self,layer,suggestion = ""):
        """Aquesta funcio obte el tipus de geometria de la taula que li passem per parametres"""
        global schema
        autoGeom = self.guessGeometryField(layer,suggestion=suggestion)
        sql='''SELECT ST_GeometryType(%s) FROM "%s"."%s";''' % (autoGeom,schema,layer)
        query = self.db.exec_(sql)
        query.next()
        res = unicode(query.value(0))
        #print res
        return res

    def getGeometryFields(self,layer):
        """Aquesta funcio obte el camp de geometria de la taula que li passem per parametres"""
        fields = self.getFieldsContent(layer)
        geomFields = []
        for field in fields:
            if self.getFieldsType(layer,field)== 'geometry':
                geomFields.append(field)
        if geomFields == []:
            return None
        else:
            return geomFields

    def guessGeometryField(self,layer,suggestion = None):
        """Aquesta funcio obte el camp de geometria de la taula que li passem per parametres"""
        if suggestion in self.getFieldsContent(layer):
           return suggestion
        else:
            try:
                return self.getGeometryFields(layer)[0]
            except:
                return None
    
    def getFieldsContent(self,layer):
        """Aquesta funcio obte el nom dels camps de la taula que li passem per parametres"""
        global schema
        sql="SELECT column_name FROM information_schema.columns WHERE table_name='%s' and table_schema='%s';" % (layer,schema)
        query = self.db.exec_(sql)
        fields=[]
        while (query.next()):
            fields.append(unicode(query.value(0)))
        if fields==[]:
            sql="SELECT attname, typname ,relname FROM pg_attribute a JOIN pg_class c on a.attrelid = c.oid JOIN pg_type t on a.atttypid = t.oid WHERE relname = '%s' and attnum >= 1;" % layer
            #print sql
            query = self.db.exec_(sql)
            while (query.next()):
                fields.append(unicode(query.value(0)))
            #print fields
        return fields
    
    def getFieldsType(self,layer,field):
        """Aquesta funcio obte el tipus del camp de la taula i el camp que li passem per parametres"""
        sql = "SELECT typname FROM pg_attribute a JOIN pg_class c on a.attrelid = c.oid JOIN pg_type t on a.atttypid = t.oid WHERE relname = '%s' and attname = '%s'" % (layer,field)
        query = self.db.exec_(sql)
        query.next()
        res = unicode(query.value(0))
        #print res
        return res

    def getGeometryField(self,layer):
        """Aquesta funcio obte el camp de geometria de la taula que li passem per parametres"""
        fields = self.getFieldsContent(layer)
        for field in fields:
            if self.getFieldsType(layer,field)== 'geometry':
                return field
        return -1
        
    def getLayers(self,schema=None):
        """Aquesta funcio cerca les entitats necessaries per fer funcionar el plugin"""
        global nomBD1
        global contra1
        global host1
        global port1
        global usuari1
        if not schema:
            schema = self.schema
        sql="select table_name from information_schema.tables where table_schema='%s';" % schema
        self.db = QSqlDatabase.addDatabase("QPSQL")
        self.db.setHostName(host1)
        self.db.setPort(int(port1))
        self.db.setDatabaseName(nomBD1)
        self.db.setUserName(usuari1)
        self.db.setPassword(contra1)
        while not self.db.open():
            print self.db.lastError().text()

        query = self.db.exec_(sql)
        layers=[]
        exclusionList = ["spatial_ref_sys","geography_columns","geometry_columns","raster_columns","raster_overviews"]
        while (query.next()):
            if not query.value(0) in exclusionList : 
                if self.getGeometryField(query.value(0)) != -1:
                    layers.append(query.value(0))
        #sql="SELECT matviewname FROM pg_matviews where schemaname='%s';"  % schema
        #query = self.db.exec_(sql)
        #while (query.next()):
        #    if self.getGeometryField(query.value(0)) != -1:
        #        layers.append(query.value(0))
        layers.sort()
        return layers
    def cercaDescripcio(self):
        """Aquesta funcio cerca els epigrafs que continguin la paraula clau que li passem"""
        global cur
        global conn        #Sentencia SQL
        self.dlg.ListaActivitatsDesc.clear()
        CAMP=chr(34)+"Descripcio epigraf"+chr(34)
        CAMP2=chr(34)+"Epigraf"+chr(34)
        TAULA="Seccio1"
        sql="SELECT "+CAMP+","+CAMP2+" FROM "+chr(34)+TAULA+chr(34)
        filtre=self.dlg.barraCerca.text()
        wheresql=" WHERE "+CAMP+" LIKE '%"+filtre+"%' order by "+CAMP+";"
        cur.execute(sql+wheresql)
        rows = cur.fetchall()
        for index,row in enumerate(rows,start=0):
            desc=row[0]
            self.dlg.ListaActivitatsDesc.addItem(desc)
            self.dlg.ListaActivitatsDesc.item(index).setToolTip(str(row[1]))
        var=cur.fetchall()
        return var;
            
        
    def ompleComboGraf(self):
        """Aquesta funcio busca les entitats que servirien com a graf"""
        global schema
        layers=self.getLayers(schema)
        #self.populateComboBox(self.dlg.GrafCombo,layers,"Select layer",True)
        myListLayers = []
        for layername in layers:
            tipus=self.getGeometryType(layername)
            if tipus in ('ST_LineString','ST_MultiLineString'):
                myListLayers.append(layername)
        #myListLayers = [layername for layername in layers if self.getGeometryType(layername) in ('ST_LineString','ST_MultiLineString')]
        self.dlg.GrafCombo.addItems( myListLayers )

    
    def cercaEpigraf(self):
        """Aquesta funcio cerca els epigrafs que continguin la paraula clau que li passem"""
        global nomBD1
        global contra1
        global host1
        global port1
        global usuari1
        global schema
        global cur
        global conn        #Sentencia SQL
        self.dlg.ListaActivitatsEpigraf.clear()
        CAMP=chr(34)+"Descripcio epigraf"+chr(34)
        CAMP2=chr(34)+"Epigraf"+chr(34)
        TAULA="Seccio1"
        sql="SELECT "+CAMP2+","+CAMP+" FROM "+chr(34)+TAULA+chr(34)
        filtre=self.dlg.barraCerca.text()
        wheresql=" ORDER BY "+CAMP2+";"
        
        try:
            cur.execute(sql+wheresql)
            rows = cur.fetchall()
            for index,row in enumerate(rows,start=0):
                desc=row[1]
                self.dlg.ListaActivitatsEpigraf.addItem(str(row[0]))
                self.dlg.ListaActivitatsEpigraf.item(index).setToolTip(desc)
            var=cur.fetchall()
            return var;
            
        except:
            self.dlg.EstatConnexio.setStyleSheet('border:1px solid #000000; background-color: #ff7f7f')
            self.dlg.EstatConnexio.setText(u'Error: Hi ha algun camp erroni en la taula Seccio1.')
            self.dlg.EstatConnexio.setToolTip(u'Error: Hi ha algun camp erroni en la taula Seccio1.')
            print "I am unable to connect to the database"
        
    # Create the actions 
    #@pyqtSlot()
    def on_click_cerca(self):
        """Aquesta es una funcio que fa una crida a una funcio auxiliar per fer una cerca entre els epigrafs"""
        self.cercaDescripcio()

    def on_click_Borra_seleccio_noms(self):
        """Aquesta funcio esborra la llista dels epigrafs seleccionats"""
        self.dlg.ListaActivitatsDesc.clearSelection()
                
    def on_click_Borra_seleccio_numeros(self):
        """Aquesta funcio esborra la llista dels numeros dels epigrafs seleccionats"""
        self.dlg.ListaActivitatsEpigraf.clearSelection()

    def on_seleccion_change_Epigrafs(self,current, previous):
        """Aquesta funcio mostra el widget de la part superior i mostra el numero d'elements seleccionats"""
        seleccio_noms=len(self.dlg.ListaActivitatsDesc.selectedItems())
        seleccio_numeros=len(self.dlg.ListaActivitatsEpigraf.selectedItems())
        #self.dlg.Seleccio.setText(u'Seleccionats: Descripció('+str(seleccio_noms)+u') - Epígraf('+str(seleccio_numeros)+")")
        self.bar.clearWidgets()
        self.bar.pushMessage("Info", u'Seleccionats: Descripció('+str(seleccio_noms)+u') - Epígraf('+str(seleccio_numeros)+")", level=QgsMessageBar.INFO)
        self.bar.layout().addWidget(self.dlg.btn_mostra_sel, 0, 0)
        self.dlg.btn_mostra_sel.setVisible(True)

    def on_seleccion_change_Desc(self,current, previous):
        """Aquesta es una funcio auxiliar que controla l'aparença d'alguns elements de la interficie"""
        seleccio_noms=len(self.dlg.ListaActivitatsDesc.selectedItems())
        seleccio_numeros=len(self.dlg.ListaActivitatsEpigraf.selectedItems())
        self.bar.clearWidgets()
        self.bar.pushMessage("Info", u'Seleccionats: Descripció('+str(seleccio_noms)+u') - Epígraf('+str(seleccio_numeros)+")", level=QgsMessageBar.INFO)
        self.bar.layout().addWidget(self.dlg.btn_mostra_sel, 0, 0)
        self.dlg.btn_mostra_sel.setVisible(True)

    def on_click_mostra_seleccio(self):
        """Aquesta es una funcio auxiliar que controla l'aparença d'alguns elements de la interficie"""
        llista_sel=self.dlg.ListaActivitatsDesc.selectedItems()
        llista_sel_EPIGRAF=self.dlg.ListaActivitatsEpigraf.selectedItems()
        llistat=""
        if (len(llista_sel)>0 or len(llista_sel_EPIGRAF)>0):
            for item in llista_sel:
                nom_desc="("+item.toolTip()+")-"+item.text()
                llistat=llistat+nom_desc+"\n"
            del llista_sel
            for item in llista_sel_EPIGRAF:
                num_epi="("+item.text()+")-"+item.toolTip()
                llistat=llistat+num_epi+"\n"
            del llista_sel_EPIGRAF
        #print llistat
        #self.bar.pushMessage("Epigrafs seleccionats:", llistat, level=QgsMessageBar.INFO)
        QMessageBox.information(None, "Epigrafs seleccionats:",llistat )
    
    #@pyqtSlot()
    def on_click_totes(self):
        """Aquesta es una funcio auxiliar que controla l'aparença d'alguns elements de la interficie"""
        self.dlg.barraCerca.setText("")
        self.cercaDescripcio()

    #@pyqtSlot()
    def on_click_List(self):
        pass
    
    #@pyqtSlot()
    def on_click_ColorTopos(self):
        """Aquesta es una funcio auxiliar que controla l'aparença d'alguns elements de la interficie"""
        global micolor_Topo
        aux = QColorDialog.getColor()
        if (aux.isValid()):
           micolor_Topo=aux 
        estilo=u'border:1px solid #000000; background-color: '+micolor_Topo.name().decode('utf8')
        self.dlg.ColorTopos.setStyleSheet(estilo)
        self.dlg.ColorTopos.setAutoFillBackground(True)

    
    #@pyqtSlot()
    def on_click_ColorZI(self):
        """Aquesta es una funcio auxiliar que controla l'aparença d'alguns elements de la interficie"""
        global micolor_ZI
        aux = QColorDialog.getColor()
        if (aux.isValid()):
           micolor_ZI=aux 
        estilo=u'border:1px solid #000000; background-color: '+micolor_ZI.name().decode('utf8')
        self.dlg.ColorZI.setStyleSheet(estilo)
        self.dlg.ColorZI.setAutoFillBackground(True)
    
    def on_click_ColorGraf(self):
        """Aquesta es una funcio auxiliar que controla l'aparença d'alguns elements de la interficie"""
        global micolor_Graf
        aux = QColorDialog.getColor()
        if (aux.isValid()):
           micolor_Graf=aux 
        estilo=u'border:1px solid #000000; background-color: '+micolor_Graf.name().decode('utf8')
        self.dlg.ColorGraf.setStyleSheet(estilo)
        self.dlg.ColorGraf.setAutoFillBackground(True)
    
    #@pyqtSlot()
    def on_click_Veure_ZI(self,state):
        """Aquesta es una funcio auxiliar que controla la visibilitat de diferents 
        elements de la interficie segons la opcio marcada"""
        if state == QtCore.Qt.Checked:
            self.dlg.Poblacio_panel.setVisible(True)
            self.dlg.VeureZI_panel.setVisible(True)
            if (self.dlg.parcela.isChecked()):
                self.dlg.ZIGraf_radio.setVisible(False)
            else:
                self.dlg.ZIGraf_radio.setVisible(True)
        else:
            self.dlg.VeureZI_panel.setVisible(False)
            self.dlg.Poblacio_panel.setVisible(False)

    def Canvia_label_ZI(self):
        """Aquesta es una funcio auxiliar que controla l'aparença d'alguns elements de la interficie"""
        if (self.dlg.GrafCombo.currentText()=="Distancia"):
            self.dlg.CostInvers_chk.setVisible(False)
            self.dlg.CostNusos.setVisible(False)
            self.dlg.label_5.setText(u'Distància (m)')
            self.dlg.Radi_ZI.setText(u'150')
        else:
            self.dlg.label_5.setText(u'Temps (min)')
            self.dlg.Radi_ZI.setText(u'2')
            self.dlg.CostNusos.setChecked(False)
            self.dlg.CostNusos.setVisible(True)
            self.dlg.CostInvers_chk.setChecked(True)
            self.dlg.CostInvers_chk.setVisible(True)
        return 0
    def on_Change_GrafCombo(self):
        """Aquesta es una funcio fa una crida a una funció auxiliar"""
        self.Canvia_label_ZI()
        
    def on_toggled_ZIGraf_radio(self,enabled):
        """Aquesta es una funcio auxiliar que controla la visibilitat de diferents 
        elements de la interficie segons la opcio marcada"""
        if enabled:
            self.dlg.ZIGraf_panel.setVisible(True)
            self.Canvia_label_ZI()
            if not(self.dlg.topo.isChecked()):
                self.dlg.Poblacio_panel.setVisible(True)
            else:
                self.dlg.Poblacio_panel.setVisible(True)
        else:
            self.dlg.ZIGraf_panel.setVisible(False)
            self.dlg.MostrarGraf_chk.setChecked(False)
            self.dlg.label_5.setText(u'Radi (m)')
            self.dlg.Radi_ZI.setText(u'150')

    def on_toggled_parcela(self,enabled):
        """Aquesta es una funcio auxiliar que controla la visibilitat de diferents 
        elements de la interficie segons la opcio marcada"""
        if enabled:
            self.dlg.CalculRadiTopos_panel.setVisible(False)
            self.dlg.ZIGraf_radio.setVisible(False)
            self.dlg.ZICirc_radio.setChecked(True)
        else:
            self.dlg.CalculRadiTopos_panel.setVisible(True)
            self.dlg.ZIGraf_radio.setVisible(True)

    def on_valuechange_Transparencia(self):
        """Aquesta es una funcio auxiliar que canvia el valor de la etiqueta associada a la transperencia de la capa escollida"""
        self.dlg.Transparencia_lbl.setText(str(self.dlg.Transparencia.value())+u' %')

    def retorna_nom_geometria(self,mylayer):
        """Aquesta es una funcio auxiliar que comprova quin es el tipus de camp de geometria"""    
        if mylayer.wkbType()==QGis.WKBPoint:
            print 'Layer is a pojnt layer'
        
        if mylayer.wkbType()==QGis.WKBLineString:
            print 'Layer is a line layer'
        
        if mylayer.wkbType()==QGis.WKBPolygon:
            print 'Layer is a polygon layer'
        
        if mylayer.wkbType()==QGis.WKBMultiPolygon:
            print 'Layer is a multi-polygon layer'
        
        if mylayer.wkbType()==100:
            print 'Layer is a data-only layer'

    #@pyqtSlot()
    def calcul_graf(self,sql_buff):
        """Aquesta es una funcio auxiliar que retorna un sql amb el buffer"""
        global micolor_Topo
        global micolor_ZI
        global micolor_Graf
        global Fitxer
        global cur
        global conn
        global progress
#       *****************************************************************************************************************
#       INICI CREACIO DE LA TAULA 'XARXA_GRAF' I PREPARACIO DELS CAMPS COST I REVERSE_COST
#       *****************************************************************************************************************
        # Preparar els camps cost i reverse_cost en funció del que es necessiti, es crearà taula local temporal per evitar problemes de concurrencia
        sql_1="DROP TABLE IF EXISTS \"Xarxa_Graf\";\n"
        """ Es fa una copia de la taula que conté el graf i s'afegeixen els camps cost i reverse_cost en funció del que es necessiti, es crearà taula local temporal per evitar problemes de concurrencia"""
        sql_1+="CREATE local temporary TABLE IF NOT EXISTS \"Xarxa_Graf\" as (SELECT * FROM \"SegmentsXarxaCarrers\");\n"
        if (self.dlg.GrafCombo.currentText()=="Distancia"):
            """S'aplica com a cost tant directe com invers el valor de la longitud del segment"""
            sql_1+="UPDATE \"Xarxa_Graf\" set \"cost\"=\"LONGITUD_SEGMENT\", \"reverse_cost\"=\"LONGITUD_SEGMENT\";\n"
        else:
            if (self.dlg.CostInvers_chk.isChecked()):
                """S'aplica com a 'cost' el valor del camp 'cost directe', i a 'reverse_cost' el valor del camp 'cost_invers"""
                #sql_1+="UPDATE \"Xarxa_Graf\" set \"cost\"=\"Cost_Directe\", \"reverse_cost\"=\"Cost_Invers\";\n"
            else:
                """S'aplica com a 'cost' i 'reverse_cost' el valor del camp 'cost directe'"""
                sql_1+="UPDATE \"Xarxa_Graf\" set \"reverse_cost\"=\"cost\";\n"
            if (self.dlg.CostNusos.isChecked()):
                """Es suma al camp 'cost' i a 'reverse_cost' el valor dels semafors sempre i quan estigui la opció marcada"""
                sql_1+="UPDATE \"Xarxa_Graf\" set \"cost\"=\"cost\"+(\"Cost_Total_Semafor_Tram\"), \"reverse_cost\"=\"reverse_cost\"+(\"Cost_Total_Semafor_Tram\");\n"
                
        print sql_1;
        cur.execute(sql_1)
        conn.commit()
#       *****************************************************************************************************************
#       FI CREACIO DE LA TAULA 'XARXA_GRAF' I PREPARACIO DELS CAMPS COST I REVERSE_COST
#       *****************************************************************************************************************

#       *****************************************************************************************************************
#       INICI CREACIO DE LA TAULA 'PUNTS_INTERES_TMP' QUE CONTINDRA ELS PUNTS D'INTERES PROJECTATS SOBRE EL TRAM
#       *****************************************************************************************************************
        geometria="the_geom"#self.campGeometria(self.dlg.comboSelPunts.currentText())
        sql_1="drop table if exists punts_interes_tmp;\n"
        """Es crea la taula punts_interes_tmp seleccionant el centroide de la entitat seleccionada, utilizant un radi fix"""
        sql_1+="CREATE local temporary TABLE if not exists punts_interes_tmp as (SELECT ST_Centroid(tmp.\""+geometria+"\") the_geom,tmp.\"ogc_fid\" as pid from ("+sql_buff+") tmp);\n"
        sql_1+="ALTER TABLE punts_interes_tmp ADD COLUMN     x FLOAT;\n"
        sql_1+="ALTER TABLE punts_interes_tmp ADD COLUMN     y FLOAT;\n"
        sql_1+="ALTER TABLE punts_interes_tmp ADD COLUMN     edge_id BIGINT;\n"
        sql_1+="ALTER TABLE punts_interes_tmp ADD COLUMN     side CHAR;\n"
        sql_1+="ALTER TABLE punts_interes_tmp ADD COLUMN     fraction FLOAT;\n"
        sql_1+="ALTER TABLE punts_interes_tmp ADD COLUMN     newPoint geometry;\n"
        
        print sql_1;
        cur.execute(sql_1)
        conn.commit()
#       *****************************************************************************************************************
#       FI CREACIO DE LA TAULA 'PUNTS_INTERES_TMP' QUE CONTINDRA ELS PUNTS D'INTERES PROJECTATS SOBRE EL TRAM
#       *****************************************************************************************************************

#       *****************************************************************************************************************
#       INICI ASSIGNACIO DEL VALOR DEL TRAM MES PROPER AL CAMP 'EDGE_ID' DE LA TAULA 'PUNTS_INTERES_TMP I LA PROJECCIO DEL PUNT D'INTERES SOBRE EL TRAM
#       *****************************************************************************************************************
        """S'assigna el valor del tram més proper al punt d'interes en el camp 'edge_id' de la taula 'punts_interes_tmp'"""
        sql_1="UPDATE \"punts_interes_tmp\" set \"edge_id\"=tram_proper.\"tram_id\" from (SELECT distinct on(Poi.pid) Poi.pid As Punt_id,Sg.id as Tram_id, ST_Distance(Sg.the_geom,Poi.the_geom)  as dist FROM \"Xarxa_Graf\" as Sg,\"punts_interes_tmp\" AS Poi ORDER BY  Poi.pid,ST_Distance(Sg.the_geom,Poi.the_geom),Sg.id) tram_proper where \"punts_interes_tmp\".\"pid\"=tram_proper.\"punt_id\";\n"
        """Es calcula la fraccio del tram que on esta situat la projecció del punt d'interes"""
        sql_1+="UPDATE \"punts_interes_tmp\" SET fraction = ST_LineLocatePoint(e.the_geom, \"punts_interes_tmp\".the_geom),newPoint = ST_LineInterpolatePoint(e.the_geom, ST_LineLocatePoint(e.the_geom, \"punts_interes_tmp\".the_geom)) FROM \"Xarxa_Graf\" AS e WHERE \"punts_interes_tmp\".\"edge_id\" = e.id;\n"
        print sql_1;
        cur.execute(sql_1)
        conn.commit()

#       *****************************************************************************************************************
#       FI ASSIGNACIO DEL VALOR DEL TRAM MES PROPER AL CAMP 'EDGE_ID' DE LA TAULA 'PUNTS_INTERES_TMP 
#       *****************************************************************************************************************

#       *****************************************************************************************************************
#       INICI DE LA CREACIO DE LA TAULA 'TBL_PUNTS_FINALS_TMP' QUE CONTINDRA ELS ID DELS NODES DE LA XARXA QUE SON A DINS DEL RADI 
#       *****************************************************************************************************************
        sql_1="DROP FUNCTION IF EXISTS Cobertura();\n"
        sql_1+="DROP TABLE IF EXISTS tbl_punts_finals_tmp;\n"

        """ Es posa a dins d'una variable 'contador' tots els pid de cada punt d'interes"""
        cur.execute("select \"pid\" from \"punts_interes_tmp\" order by \"pid\" asc ;\n")
        contador = cur.fetchall()            
        sql_1+="CREATE local temporary TABLE IF NOT EXISTS tbl_punts_finals_tmp (node BIGINT,agg_cost FLOAT,start_vid BIGINT);\n"
        cur.execute(sql_1)
        conn.commit()
        for x in range (0,len(contador)):
            sql="insert into tbl_punts_finals_tmp SELECT node,agg_cost,start_vid FROM pgr_withPointsDD('SELECT id, source, target, cost, reverse_cost FROM \"Xarxa_Graf\" ORDER BY id','SELECT pid, edge_id, fraction, side from \"punts_interes_tmp\"',array[-"+str(contador[x][0])+"],"+self.dlg.Radi_ZI.text()+",driving_side := 'b',details := false);\n"
            cur.execute(sql)
            conn.commit()
#        for x in range (0,len(contador)):
#            if (x!=0):
#                sql_1+=" UNION "
#            sql_1+="SELECT node,agg_cost,start_vid FROM pgr_withPointsDD('SELECT id, source, target, cost, reverse_cost FROM \"Xarxa_Graf\" ORDER BY id','SELECT pid, edge_id, fraction, side from \"punts_interes_tmp\"',array[-"+str(contador[x][0])+"],"+self.dlg.Radi_ZI.text()+",driving_side := 'b',details := false)"
#        sql_1+=");\n"
        #print sql_1
        """Creació de la taula 'tbl_punts_finsl_tmp' on es tindrà tots els nodes de la xarxa que son a dins del radi fix d'acció indicat"""
        #sql_1+="CREATE local temporary TABLE IF NOT EXISTS tbl_punts_finals_tmp AS(SELECT node,agg_cost,start_vid FROM pgr_withPointsDD('SELECT id, source, target, cost, reverse_cost FROM \"Xarxa_Graf\" ORDER BY id','SELECT pid, edge_id, fraction, side from \"punts_interes_tmp\"',array(select \"pid\"*(-1) from \"punts_interes_tmp\"),"+self.dlg.Radi_ZI.text()+",driving_side := 'b',details := false));\n"

#       *****************************************************************************************************************
#       FI DE LA CREACIO DE LA TAULA 'TBL_PUNTS_FINALS_TMP' QUE CONTINDRA ELS ID DELS NODES DE LA XARXA QUE SON A DINS DEL RADI 
#       *****************************************************************************************************************
#       *****************************************************************************************************************
#       INICI DE LA CREACIO DE LA TAULA 'GEO_PUNTS_FINALS_TMP' QUE CONTINDRA ELS NODES DE LA XARXA QUE SON A DINS DEL RADI 
#       *****************************************************************************************************************
        sql_1="DROP table if exists geo_punts_finals_tmp;\n"
        """Creació de la taula 'geo_punts_finals_tmp' on estan tots els nodes de la xarxa que son a dins del radi fix amb la geometria inclosa"""
        sql_1+="CREATE local temporary TABLE IF NOT EXISTS geo_punts_finals_tmp as (select \"SegmentsXarxaCarrers_vertices_pgr\".*,\"tbl_punts_finals_tmp\".\"agg_cost\", \"tbl_punts_finals_tmp\".\"start_vid\" from \"SegmentsXarxaCarrers_vertices_pgr\",\"tbl_punts_finals_tmp\" where \"SegmentsXarxaCarrers_vertices_pgr\".\"id\" =\"tbl_punts_finals_tmp\".\"node\");\n"
#       *****************************************************************************************************************
#       FI DE LA CREACIO DE LA TAULA 'GEO_PUNTS_FINALS_TMP' QUE CONTINDRA ELS NODES DE LA XARXA QUE SON A DINS DEL RADI 
#       *****************************************************************************************************************
            
        
#       *****************************************************************************************************************
#       INICI DE LA CREACIO DE LA TAULA 'TRAMS_FINALS_TMP' QUE CONTINDRA ELS TRAMS QUE FORMEN PART DEL RADI D'ACCIO INDICAT 
#       *****************************************************************************************************************
        sql_1+="DROP table IF EXISTS trams_finals_tmp;\n"
        if (self.dlg.GrafCombo.currentText()=="Distancia"):
            """Si s'ha escollit calcula mitjançant distancia """
            """Creació de la taula que contindrà els trams que formen part del radi d'acció indicat, si el radi escollit es un radi fix"""
            sql_1+="CREATE local temporary TABLE IF NOT EXISTS trams_finals_tmp as (select \"Xarxa_Graf\".\"id\",\"Xarxa_Graf\".\"the_geom\",\"geo_punts_finals_tmp\".\"id\" as node,\"geo_punts_finals_tmp\".\"agg_cost\" as coste,("+self.dlg.Radi_ZI.text()+"-\"geo_punts_finals_tmp\".\"agg_cost\") as falta,\"geo_punts_finals_tmp\".\"start_vid\" as id_punt, (select case when ("+self.dlg.Radi_ZI.text()+"-\"geo_punts_finals_tmp\".\"agg_cost\")/ST_Length(\"Xarxa_Graf\".\"the_geom\")<=1 then ("+self.dlg.Radi_ZI.text()+"-\"geo_punts_finals_tmp\".\"agg_cost\")/ST_Length(\"Xarxa_Graf\".\"the_geom\") when ("+self.dlg.Radi_ZI.text()+"-\"geo_punts_finals_tmp\".\"agg_cost\")/ST_Length(\"Xarxa_Graf\".\"the_geom\")>1 then (1) end) as fraccio from \"Xarxa_Graf\",\"geo_punts_finals_tmp\" where ST_DWithin(\"geo_punts_finals_tmp\".\"the_geom\",\"Xarxa_Graf\".\"the_geom\",1)=TRUE);\n"
        else:                
            """Si s'ha escollit calcula mitjançant Temps """
            if (self.dlg.CostInvers_chk.isChecked()):
                """Creació de la taula que contindrà els trams que formen part del radi d'acció indicat, si el radi escollit es un radi fix"""
                sql_1+="CREATE local temporary TABLE IF NOT EXISTS trams_finals_tmp as (select \"Xarxa_Graf\".\"id\",\"Xarxa_Graf\".\"cost\",\"Xarxa_Graf\".\"reverse_cost\",\"Xarxa_Graf\".\"the_geom\",\"geo_punts_finals_tmp\".\"id\" as node,\"geo_punts_finals_tmp\".\"agg_cost\" as coste,("+self.dlg.Radi_ZI.text()+"-\"geo_punts_finals_tmp\".\"agg_cost\") as falta,\"geo_punts_finals_tmp\".\"start_vid\" as id_punt, (select case when (("+self.dlg.Radi_ZI.text()+"-\"geo_punts_finals_tmp\".\"agg_cost\")/(CASE WHEN \"geo_punts_finals_tmp\".\"id\"=\"Xarxa_Graf\".\"target\" THEN \"Xarxa_Graf\".\"reverse_cost\" ELSE \"Xarxa_Graf\".\"cost\" END))<=1 then (("+self.dlg.Radi_ZI.text()+"-\"geo_punts_finals_tmp\".\"agg_cost\")/(CASE WHEN \"geo_punts_finals_tmp\".\"id\"=\"Xarxa_Graf\".\"target\" THEN \"Xarxa_Graf\".\"reverse_cost\" ELSE \"Xarxa_Graf\".\"cost\" END)) when (("+self.dlg.Radi_ZI.text()+"-\"geo_punts_finals_tmp\".\"agg_cost\")/(CASE WHEN \"geo_punts_finals_tmp\".\"id\"=\"Xarxa_Graf\".\"target\" THEN \"Xarxa_Graf\".\"reverse_cost\" ELSE \"Xarxa_Graf\".\"cost\" END))>1 then (1) end) as fraccio from \"Xarxa_Graf\",\"geo_punts_finals_tmp\" where ST_DWithin(\"geo_punts_finals_tmp\".\"the_geom\",\"Xarxa_Graf\".\"the_geom\",1)=TRUE);\n"
            else:
                """Creació de la taula que contindrà els trams que formen part del radi d'acció indicat, si el radi escollit es un radi fix"""
                sql_1+="CREATE local temporary TABLE IF NOT EXISTS trams_finals_tmp as (select \"Xarxa_Graf\".\"id\",\"Xarxa_Graf\".\"cost\",\"Xarxa_Graf\".\"reverse_cost\",\"Xarxa_Graf\".\"the_geom\",\"geo_punts_finals_tmp\".\"id\" as node,\"geo_punts_finals_tmp\".\"agg_cost\" as coste,("+self.dlg.Radi_ZI.text()+"-\"geo_punts_finals_tmp\".\"agg_cost\") as falta,\"geo_punts_finals_tmp\".\"start_vid\" as id_punt, (select case when (("+self.dlg.Radi_ZI.text()+"-\"geo_punts_finals_tmp\".\"agg_cost\")/(\"Xarxa_Graf\".\"cost\"))<=1 then (("+self.dlg.Radi_ZI.text()+"-\"geo_punts_finals_tmp\".\"agg_cost\")/(\"Xarxa_Graf\".\"cost\")) when (("+self.dlg.Radi_ZI.text()+"-\"geo_punts_finals_tmp\".\"agg_cost\")/(\"Xarxa_Graf\".\"cost\"))>1 then (1) end) as fraccio from \"Xarxa_Graf\",\"geo_punts_finals_tmp\" where ST_DWithin(\"geo_punts_finals_tmp\".\"the_geom\",\"Xarxa_Graf\".\"the_geom\",1)=TRUE);\n"
            
        cur.execute(sql_1)
        conn.commit()

#       *****************************************************************************************************************
#       FI DE LA CREACIO DE LA TAULA 'TRAMS_FINALS_TMP' QUE CONTINDRA ELS TRAMS QUE FORMEN PART DEL RADI D'ACCIO INDICAT 
#       *****************************************************************************************************************

#       *****************************************************************************************************************
#       INICI FUNCIO PER CREAR ELS TRAMS FINALS AMB LA FRACCIO DE TRAM QUE LI CORRESPON 
#       *****************************************************************************************************************
        sql_1="DROP FUNCTION IF EXISTS Cobertura();\n"
        sql_1+="CREATE OR REPLACE FUNCTION Cobertura() RETURNS SETOF trams_finals_tmp AS\n"
        sql_1+="$BODY$\n"
        sql_1+="DECLARE\n"
        sql_1+="r trams_finals_tmp%rowtype;\n"
        sql_1+="m trams_finals_tmp%rowtype;\n"
        sql_1+="BEGIN\n"
        sql_1+="DROP TABLE IF EXISTS fraccio_trams_raw;\n"
        sql_1+="CREATE local temporary TABLE fraccio_trams_raw (the_geom geometry, punt_id bigint,id_tram bigint,fraccio FLOAT,node bigint,fraccio_inicial FLOAT,cost_invers FLOAT,cost_directe FLOAT,target bigint);\n"
        sql_1+="FOR r IN SELECT \"trams_finals_tmp\".* FROM \"trams_finals_tmp\" WHERE \"trams_finals_tmp\".\"id\" not in (select \"edge_id\" from \"punts_interes_tmp\")\n"
        sql_1+="LOOP\n"
        sql_1+="insert into fraccio_trams_raw VALUES(ST_Line_Substring((r.\"the_geom\"),"
        sql_1+="case when (select ST_Line_Locate_Point((r.\"the_geom\"),(select \"geo_punts_finals_tmp\".\"the_geom\" from \"geo_punts_finals_tmp\" where \"geo_punts_finals_tmp\".\"id\"=r.\"node\" and \"geo_punts_finals_tmp\".\"start_vid\"=r.\"id_punt\")))<0.001 then 0 else 1-r.\"fraccio\"\n"
        sql_1+="END,\n"
        sql_1+="case when (select ST_Line_Locate_Point((r.\"the_geom\"),(select \"geo_punts_finals_tmp\".\"the_geom\" from \"geo_punts_finals_tmp\" where \"geo_punts_finals_tmp\".\"id\"=r.\"node\" and \"geo_punts_finals_tmp\".\"start_vid\"=r.\"id_punt\")))<0.001 then r.\"fraccio\" else 1\n"
        sql_1+="END),r.\"id_punt\"*(-1),r.\"id\",0,r.\"node\",0,0,0);\n"
        sql_1+="RETURN NEXT r;\n"
        sql_1+="END LOOP;\n"

        sql_1+="FOR m IN SELECT \"trams_finals_tmp\".* FROM \"trams_finals_tmp\" WHERE \"trams_finals_tmp\".\"id\" in (select \"edge_id\" from \"punts_interes_tmp\")\n"
        sql_1+="LOOP\n"
        sql_1+="insert into fraccio_trams_raw VALUES(m.\"the_geom\",m.\"id_punt\"*(-1),m.\"id\",0,m.\"node\",0,0,0);\n"

        sql_1+="RETURN NEXT m;\n"
        sql_1+="END LOOP;\n"

        sql_1+="RETURN;\n"
        sql_1+="END\n"
        sql_1+="$BODY$\n"
        sql_1+="LANGUAGE 'plpgsql' ;\n"
        
        sql_1+="SELECT \"the_geom\" FROM Cobertura();\n"
        self.dlg.Progres.setValue(45)
        progress.setValue(45)

        qApp.processEvents()
        cur.execute(sql_1)
        conn.commit()


#       *****************************************************************************************************************
#       FI FUNCIO PER CREAR ELS TRAMS FINALS AMB LA FRACCIO DE TRAM QUE LI CORRESPON 
#       *****************************************************************************************************************

#       *****************************************************************************************************************
#       INICI ACTUALITZACIO DE LA FRACCIO DELS TRAMS INICIALS 
#       *****************************************************************************************************************
        """Actualització de la fracció dels trams inicials  """
        sql_1="update \"fraccio_trams_raw\" set \"fraccio_inicial\"=\"punts_interes_tmp\".\"fraction\" from \"punts_interes_tmp\" where \"id_tram\"=\"edge_id\""
        cur.execute(sql_1)
        conn.commit()

#       *****************************************************************************************************************
#       FI ACTUALITZACIO DE LA FRACCIO DELS TRAMS INICIALS 
#       *****************************************************************************************************************

#       *****************************************************************************************************************
#       INICI ACTUALITZACIO DELS VALORS DE COST DIRECTE, TARGET, COST INVERS DELS TRAMS INICIALS 
#       *****************************************************************************************************************
        """Actualització dels valors de cost directe, target, cost invers dels trams inicials"""
        sql_1="update \"fraccio_trams_raw\" set \"cost_directe\"=\"Xarxa_Graf\".\"cost\",\"target\"=\"Xarxa_Graf\".\"target\",\"cost_invers\"=\"Xarxa_Graf\".\"reverse_cost\" from \"Xarxa_Graf\" where \"id_tram\"=\"id\""
        cur.execute(sql_1)
        conn.commit()
#       *****************************************************************************************************************
#       FI ACTUALITZACIO DELS VALORS DE COST DIRECTE, TARGET, COST INVERS DELS TRAMS INICIALS 
#       *****************************************************************************************************************

        
#       *****************************************************************************************************************
#       INICI CALCUL DE LA FRACCIO DE CADA TRAM FINAL 
#       *****************************************************************************************************************
        if (self.dlg.GrafCombo.currentText()!="Distancia"):
            """Calcul del la fracció final de cada tram en el cas d'haber escollit temps"""
            cost_tram="(CASE WHEN \"geo_punts_finals_tmp\".\"id\"=\"fraccio_trams_raw\".\"target\" THEN \"fraccio_trams_raw\".\"cost_invers\" ELSE \"fraccio_trams_raw\".\"cost_directe\" END)"
            where_tram=" FROM \"geo_punts_finals_tmp\" WHERE ST_DWithin(\"geo_punts_finals_tmp\".\"the_geom\",\"fraccio_trams_raw\".\"the_geom\",1)=TRUE"
        else:
            """Calcul del la fracció final de cada tram en el cas d'haber escollit distancia"""
            cost_tram="ST_Length(\"fraccio_trams_raw\".\"the_geom\")"
            where_tram=""
            
        sql_1="UPDATE \"fraccio_trams_raw\" SET \"fraccio\"=" 
        sql_1+="((case when (\"fraccio_trams_raw\".\"fraccio_inicial\"*"+cost_tram+")>"+self.dlg.Radi_ZI.text()+" then ("+self.dlg.Radi_ZI.text()+"/"+cost_tram+") else \"fraccio_trams_raw\".\"fraccio_inicial\" end)"
        sql_1+="+"
        sql_1+="(case when ((1-\"fraccio_trams_raw\".\"fraccio_inicial\")*"+cost_tram+")>"+self.dlg.Radi_ZI.text()+" then ("+self.dlg.Radi_ZI.text()+"/"+cost_tram+") else (1-\"fraccio_trams_raw\".\"fraccio_inicial\") end))"
        sql_1+=where_tram+";\n"
        print sql_1
        cur.execute(sql_1)
        conn.commit()
        
#       *****************************************************************************************************************
#       FI CALCUL DE LA FRACCIO DE CADA TRAM FINAL 
#       *****************************************************************************************************************

#       *****************************************************************************************************************
#       INICI MODIFICACIO DE LA GEOMETRIA DELS TRAMS FINALS SEGONS LA FRACCIO CALCULADA 
#       *****************************************************************************************************************
        """Es modifiquen els trams finals del trajecte segons el que falti per arribar al cost desitjat"""
        sql_1="update \"fraccio_trams_raw\" set \"the_geom\"=final.\"the_geom\"" 
        sql_1+="from"
        sql_1+="(select distinct(ST_Line_Substring("
        sql_1+="(m.\"the_geom\")"
        sql_1+=","
        sql_1+="(case when (select ST_Line_Locate_Point((m.\"the_geom\"),(select \"the_geom\" from \"geo_punts_finals_tmp\" where \"geo_punts_finals_tmp\".\"id\"=m.\"node\" and \"geo_punts_finals_tmp\".\"start_vid\"=m.\"punt_id\"*-1)))<0.01 then 0 else 1-m.\"fraccio\" END)"
        sql_1+=","
        sql_1+="(case when (select ST_Line_Locate_Point((m.\"the_geom\"),(select \"the_geom\" from \"geo_punts_finals_tmp\" where \"geo_punts_finals_tmp\".\"id\"=m.\"node\" and \"geo_punts_finals_tmp\".\"start_vid\"=m.\"punt_id\"*-1)))<0.01 then m.\"fraccio\" else 1 END)"
        sql_1+="))  the_geom"
        sql_1+=","
        sql_1+="m.\"id_tram\""
        sql_1+="from \"fraccio_trams_raw\" m "
        sql_1+="where m.\"id_tram\" in (select \"edge_id\" from \"punts_interes_tmp\")) final "
        sql_1+="where final.\"id_tram\" =\"fraccio_trams_raw\".\"id_tram\";\n"
        self.dlg.Progres.setValue(55)
        progress.setValue(55)
        qApp.processEvents()
        
        cur.execute(sql_1)
        conn.commit()
#       *****************************************************************************************************************
#       FI MODIFICACIO DE LA GEOMETRIA DELS TRAMS FINALS SEGONS LA FRACCIO CALCULADA 
#       *****************************************************************************************************************
        
#       *****************************************************************************************************************
#       INICI INSERTAR ELS TRAMS INICIALS DELS QUE PARTIRA EL GRAF 
#       *****************************************************************************************************************
        """S'afegeixen els trams inicials de cada graf per modificarlos posteriorment"""
        #sql_1="insert into \"fraccio_trams_raw\" (select SX.\"the_geom\",PI.\"pid\" as punt_id,SX.\"id\"as id_tram,999 as fraccio,SX.\"source\" as node,PI.\"fraction\" as fraccio_inicial from \"SegmentsXarxaCarrers\" SX inner join (Select \"edge_id\",\"pid\",\"fraction\" from \"punts_interes_tmp\") PI on SX.\"id\"=PI.\"edge_id\");\n"
        sql_1="insert into \"fraccio_trams_raw\" (select SX.\"the_geom\",PI.\"pid\" as punt_id,SX.\"id\"as id_tram,999 as fraccio,SX.\"source\" as node,PI.\"fraction\" as fraccio_inicial,SX.\"cost\",SX.\"reverse_cost\" from \"Xarxa_Graf\" SX inner join (Select \"edge_id\",\"pid\",\"fraction\" from \"punts_interes_tmp\") PI on SX.\"id\"=PI.\"edge_id\");\n"
        
        cur.execute(sql_1)
        conn.commit()
#       *****************************************************************************************************************
#       FI INSERTAR ELS TRAMS INICIALS DELS QUE PARTIRA EL GRAF 
#       *****************************************************************************************************************

#       *****************************************************************************************************************
#       INICI MODIFICACIO DELS TRAMS INICIALS EN EL CAS QUE LA DISTANCIA A RECORRER SIGUI MES PETITA QUE EL PROPI TRAM 
#       *****************************************************************************************************************

        if (self.dlg.GrafCombo.currentText()=="Distancia"):
            """ Calcul amb distancia i radi fix"""
            cost_tram="ST_Length(SXI.\"the_geom\")"
            sql_1="UPDATE \"fraccio_trams_raw\" set \"the_geom\"=final.\"the_geom\" from (select ST_Line_Substring((SXI.\"the_geom\"),"
            sql_1+="(case when (FT.\"fraccio_inicial\"-("+self.dlg.Radi_ZI.text()+"/"+cost_tram+"))>0 then (FT.\"fraccio_inicial\"-("+self.dlg.Radi_ZI.text()+"/"+cost_tram+")) else 0 end)"
            sql_1+=","
            sql_1+="(case when (FT.\"fraccio_inicial\"+("+self.dlg.Radi_ZI.text()+"/"+cost_tram+"))<1 then (FT.\"fraccio_inicial\"+("+self.dlg.Radi_ZI.text()+"/"+cost_tram+")) else 1 end)"
            sql_1+=") as the_geom, FT.\"punt_id\",FT.\"id_tram\",FT.\"fraccio\" "
            sql_1+="from \"fraccio_trams_raw\"FT inner join (select SX.\"the_geom\" as the_geom,SX.\"id\" as tram_xarxa from \"SegmentsXarxaCarrers\" SX, \"punts_interes_tmp\" PI where SX.\"id\"=PI.\"edge_id\") SXI on FT.\"id_tram\"=SXI.tram_xarxa where FT.\"fraccio\"=999) final"
            sql_1+=" where \"fraccio_trams_raw\".\"punt_id\"=final.\"punt_id\" and \"fraccio_trams_raw\".\"fraccio\"=999;\n"
        else:
            """ Calcul amb temps i radi fix"""
            sql_1="UPDATE \"fraccio_trams_raw\" set \"the_geom\"=final.\"the_geom\" from "
            sql_1+="(select ST_Union(TOT.the_geom) the_geom,TOT.\"punt_id\" from (select ST_Line_Substring((SXI.\"the_geom\"),"
            sql_1+="(case when (FT.\"fraccio_inicial\"-("+self.dlg.Radi_ZI.text()+"/(FT.\"cost_invers\")))>0 then (FT.\"fraccio_inicial\"-("+self.dlg.Radi_ZI.text()+"/(FT.\"cost_invers\"))) else 0 end)"
            sql_1+=","
            sql_1+="FT.\"fraccio_inicial\""
            sql_1+=") as the_geom, FT.\"punt_id\" "
            sql_1+="from \"fraccio_trams_raw\"FT inner join (select SX.\"the_geom\" as the_geom,SX.\"id\" as tram_xarxa from \"SegmentsXarxaCarrers\" SX, \"punts_interes_tmp\" PI where SX.\"id\"=PI.\"edge_id\") SXI on FT.\"id_tram\"=SXI.tram_xarxa where FT.\"fraccio\"=999"
            sql_1+="UNION "
            sql_1+="select ST_Line_Substring((SXI.\"the_geom\"),"
            sql_1+="FT.\"fraccio_inicial\""
            sql_1+=","
            sql_1+="(case when (FT.\"fraccio_inicial\"+("+self.dlg.Radi_ZI.text()+"/(FT.\"cost_directe\")))<1 then (FT.\"fraccio_inicial\"+("+self.dlg.Radi_ZI.text()+"/(FT.\"cost_directe\"))) else 1 end)"
            sql_1+=") as the_geom, FT.\"punt_id\" "
            sql_1+="from \"fraccio_trams_raw\"FT inner join (select SX.\"the_geom\" as the_geom,SX.\"id\" as tram_xarxa from \"SegmentsXarxaCarrers\" SX, \"punts_interes_tmp\" PI where SX.\"id\"=PI.\"edge_id\") SXI on FT.\"id_tram\"=SXI.tram_xarxa where FT.\"fraccio\"=999) TOT GROUP BY TOT.\"punt_id\") final"
            sql_1+=" where \"fraccio_trams_raw\".\"punt_id\"=final.\"punt_id\" and \"fraccio_trams_raw\".\"fraccio\"=999;\n"
        
        cur.execute(sql_1)
        conn.commit()
#       *****************************************************************************************************************
#       FI MODIFICACIO DELS TRAMS INICIALS EN EL CAS QUE LA DISTANCIA A RECORRER SIGUI MES PETITA QUE EL PROPI TRAM 
#       *****************************************************************************************************************

#       *****************************************************************************************************************
#       INICI CREACIO TAULA FRACCIO_TRAMS_TMP I ELIMINACIO DE TRAMS DUPLICATS 
#       *****************************************************************************************************************
        sql_1+="DROP TABLE IF EXISTS fraccio_trams_tmp;\n"

        """Eliminació de trams duplicats"""
        sql_1+="CREATE local temporary TABLE fraccio_trams_tmp AS (select distinct(the_geom),punt_id from fraccio_trams_raw);\n"
        
        cur.execute(sql_1)
        conn.commit()

#       *****************************************************************************************************************
#       FI CREACIO TAULA FRACCIO_TRAMS_TMP I ELIMINACIO DE TRAMS DUPLICATS 
#       *****************************************************************************************************************

#       *****************************************************************************************************************
#       INICI CREACIO TAULA GRAF_UTILITZAT_(DATA) QUE CONTINDRA ELS TRAMS UNITS DEL GRAF 
#       *****************************************************************************************************************
        """ Es fa la unió de tots els trams des del servidor POSTGRES dins de la taula Graf_utilitzat_(data)"""
        sql_1="drop table if exists Graf_utilitzat_"+Fitxer+";\n"
        sql_1+="CREATE TABLE IF NOT EXISTS Graf_utilitzat_"+Fitxer+" AS (Select ST_Union(TOT.the_geom) the_geom, TOT.\"punt_id\" from (select the_geom,punt_id from fraccio_trams_tmp) TOT group by TOT.\"punt_id\");\n"
        cur.execute(sql_1)
        conn.commit()

#       *****************************************************************************************************************
#       FI CREACIO TAULA GRAF_UTILITZAT_(DATA) QUE CONTINDRA ELS TRAMS UNITS DEL GRAF 
#       *****************************************************************************************************************

#       *****************************************************************************************************************
#       INICI CREACIO TAULA BUFFER_FINAL_(DATA) QUE CONTINDRA EL BUFFER DE LA UNIO DELS TRAMS 
#       *****************************************************************************************************************
        sql_1+="drop table if exists Buffer_Final_"+Fitxer+";\n"
        sql_1+="CREATE TABLE IF NOT EXISTS Buffer_Final_"+Fitxer+" AS (Select ST_Union(TOT.the_geom) the_geom, TOT.\"punt_id\" from (Select ST_Buffer(the_geom,"+self.dlg.Radi_ZI_3.text()+") the_geom,punt_id from fraccio_trams_tmp)TOT group by TOT.\"punt_id\");\n"
            
        cur.execute(sql_1)
        conn.commit()
#       *****************************************************************************************************************
#       FI CREACIO TAULA BUFFER_FINAL_(DATA) QUE CONTINDRA EL BUFFER DE LA UNIO DELS TRAMS 
#       *****************************************************************************************************************

        if (self.dlg.MostrarGraf_chk.isChecked()):
            pass
        else: 
            sql_1="drop table if exists Graf_utilitzat_"+Fitxer+";\n"
            cur.execute(sql_1)
            conn.commit()
        sql_total="SELECT * FROM Buffer_Final_"+Fitxer
        return sql_total

    def on_click_INICI(self):
        """Aquesta funcio genera tots els calculs amb tots el parametres que li hem introduit
        a la finestra a traves dels elements de la interficie."""
        global nomBD1
        global contra1
        global host1
        global port1
        global usuari1
        global micolor_Topo
        global micolor_ZI
        global micolor_Graf
        global Fitxer
        global cur
        global conn
        global progress
        global Auto_generacio
        global path_file
        global Auto_primera_vegada
        global mes
        #global ArxiuTrobat
        #self.dlg.Progres.setVisible(False)
        Fitxer=datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        consoleWidget = iface.mainWindow().findChild( QDockWidget, 'PythonConsole' )
        if consoleWidget is None:
            qgis.utils.iface.actionShowPythonDialog().trigger()
            qApp.processEvents()
            consoleWidget = iface.mainWindow().findChild( QDockWidget, 'PythonConsole' )
            consoleWidget.console.shellOut.clearConsole()
            consoleWidget.setVisible( False )

        arxiuLlegit = False
        self.dlg.Progres.setValue(0)
        #progress.setValue(0)
        
        self.dlg.Progres.setVisible(False)
        self.dlg.EstatConnexioFixa.setText(u'Processant:')
        qApp.processEvents()
#       *****************************************************************************************************************
#       INICI CREACIO DE LES TAULES RESUM DESDE EL CSV SUMINISTRAT 
#       *****************************************************************************************************************
        if (self.dlg.RelacionarPoblacio.isChecked()):
            if Auto_generacio==False or (Auto_generacio==True and Auto_primera_vegada==True):
                path_file = QtGui.QFileDialog.getExistingDirectory(self.dlg,
                        u"Busca la carpeta que conté els arxius provinents del mòdul TAULA RESUM", Path_Inicial+"\\",
                        QtGui.QFileDialog.ShowDirsOnly)
                Auto_primera_vegada=False
            #ArxiuTrobat = True
            while True:
                if (path_file != ''):
                    if (os.path.exists(path_file + "\\tr_illes.csv")):
                        #ArxiuTrobat = False 
                        
                        arxiu = open(path_file + "\\tr_illes.csv", 'r')
                        arxiu.readline()
                        lines = arxiu.readlines()
                        try:
                            cur.execute("CREATE TABLE \"Resum_Temp_"+Fitxer+"\" (\"ILLES_Codificades\" varchar(20), \"Habitants\" numeric);")
                            conn.commit()
                            insert=""
                            for linia in lines:
                                vec = linia.split(';', 20 )
                                insert += "INSERT INTO \"Resum_Temp_"+Fitxer+"\" (\"ILLES_Codificades\", \"Habitants\") VALUES ('"+ vec[0] + "', "+ vec[1]+ ");\n"
                            cur.execute(insert)
                            conn.commit()
                            #print "ok"                
                        except:
                            print "I am unable to connect to the database"
                        arxiu.close()
                        arxiuLlegit = True
                        break
                    else:
                        print "No hi ha l'arxiu"
                        path_file = QtGui.QFileDialog.getExistingDirectory(self.dlg,u"Busca la carpeta que conté els arxius provinents del mòdul TAULA RESUM", Path_Inicial+"\\",QtGui.QFileDialog.ShowDirsOnly)
                else:
                    print "Cancelat"
                    #ArxiuTrobat = False
                    self.dlg.Progres.setVisible(False)
                    break
#       *****************************************************************************************************************
#       FI CREACIO DE LES TAULES RESUM DESDE EL CSV SUMINISTRAT 
#       *****************************************************************************************************************
        a=time.time()
        self.dlg.btn_mostra_sel.setVisible(False)
        progressMessageBar = self.bar.createMessage(u'Processant:')
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        progressMessageBar.layout().addWidget(progress)
        self.bar.pushWidget(progressMessageBar, self.bar.INFO)    
        self.bar.setEnabled(False)
    
        progress.setValue(10)
        self.dlg.Progres.setValue(10)
        qApp.processEvents()
        
        fesCalcul = True      
        if (self.dlg.RelacionarPoblacio.isChecked() and not arxiuLlegit):
            fesCalcul = False
        elif (self.dlg.RelacionarPoblacio.isChecked() and arxiuLlegit):
            fesCalcul = True
        else:
            fesCalcul = True
        if not(fesCalcul):
            return
            
        if (self.dlg.EstatConnexio.text()=='Connectat'): 
            self.dlg.EstatConnexio.setStyleSheet('border:1px solid #000000; background-color: rgb(255, 170, 142)')
            self.dlg.EstatConnexio.setText(u'Connectat i processant')
            llista_sel=self.dlg.ListaActivitatsDesc.selectedItems()
            llista_sel_EPIGRAF=self.dlg.ListaActivitatsEpigraf.selectedItems()
            if (len(llista_sel)>0 or len(llista_sel_EPIGRAF)>0):
                where_sentence="("
                for item in llista_sel:
                    where_sentence=where_sentence+"'"+item.toolTip()+"',"
                del llista_sel
                for item in llista_sel_EPIGRAF:
                    where_sentence=where_sentence+"'"+str(item.text())+"',"
                del llista_sel_EPIGRAF
                where_sentence=where_sentence[:-1]+")"
                #print where_sentence
                if (self.dlg.topo.isChecked()):
                    sql="SELECT BC.\"id\",BC.\"EPIGRAFIAE\",DI.\"Carrer_Num_Bis\",DI.\"REF_CADAST\",DI.\"geom\",BC.\"NumPol\",BC.\"METRES2\",("+self.dlg.texte_2.text()+"*SQRT(BC.\"METRES2\"/ PI())) AS RADI FROM (select * from \"BrossaComercial\" "
                    wheresql="where \"EPIGRAFIAE\" in "+where_sentence+") BC LEFT JOIN \"dintreilla\" DI ON (BC.\"NumPol\" = DI.\"Carrer_Num_Bis\")"
                    if (self.dlg.Mostra_punt_chk.isChecked()):
                        sql_total="select TOT.\"EPIGRAFIAE\",TOT.\"Carrer_Num_Bis\",TOT.\"REF_CADAST\",TOT.\"NumPol\",TOT.\"METRES2\",TOT.\"radi\",TOT.\"id\" AS \"ogc_fid\",TOT.\"geom\" AS the_geom from ("+sql+wheresql+") TOT"
                    else:
                        sql_total="select TOT.\"EPIGRAFIAE\",TOT.\"Carrer_Num_Bis\",TOT.\"REF_CADAST\",TOT.\"NumPol\",TOT.\"METRES2\",TOT.\"radi\",TOT.\"id\" AS \"ogc_fid\",ST_Buffer(TOT.\"geom\",TOT.\"radi\"::double precision) AS the_geom from ("+sql+wheresql+") TOT"
                else:
                    sql="SELECT PA.\"geom\",PACOUNT.\"numae\",PA.\"UTM\" FROM (SELECT count(BC.\"EPIGRAFIAE\") as numAE , PA.\"UTM\" FROM (select * from \"BrossaComercial\" where \"EPIGRAFIAE\" in "+where_sentence+") BC LEFT JOIN \"parcel\" PA ON (BC.\"CADASREF\" = PA.\"UTM\") WHERE (PA.\"UTM\" IS NOT NULL) AND (PA.\"UTM\"<>' ')  GROUP BY PA.\"UTM\") PACOUNT LEFT JOIN \"parcel\" PA ON (PACOUNT.\"UTM\"=PA.\"UTM\") WHERE (PACOUNT.\"numae\">0) "
                    sql_total="select TOT.\"UTM\" AS \"ogc_fid\",TOT.\"numae\",TOT.\"geom\" as the_geom from ("+sql+") TOT"
                    
                uri = QgsDataSourceURI()
                #print sql_total
                try:
                    uri.setConnection(host1,port1,nomBD1,usuari1,contra1)
                    print "Connectat"
                except:
                    print "Error a la connexio"
                uri.setDataSource("","("+sql_total+")","the_geom","","ogc_fid")
                titol=self.dlg.texte_3.text().replace("'","\'")
                #titol2=titol.replace("'","\'")
                if Auto_generacio==False:
                    titol3="Número de policia amb activitat: "+titol.encode('utf8','strict')
                else:
                    titol3=titol.encode('utf8','strict')
                    cur.execute("DROP TABLE IF EXISTS \""+titol3+"\";")
                    conn.commit()
                    cur.execute("CREATE TABLE \""+titol3+"\" AS ("+sql_total+");")
                    conn.commit()
                    cur.execute("COMMENT ON TABLE \""+titol3+"\" IS '"+titol3+" "+mes[date.today().month]+" "+str(date.today().year)+"';")
                    conn.commit()                            
                
                vlayer = QgsVectorLayer(uri.uri(), titol3.decode('utf8'), "postgres")
                #self.retorna_nom_geometria(vlayer)
                
                if vlayer.isValid():
                    NumPol=datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                    error=QgsVectorFileWriter.writeAsVectorFormat(vlayer, os.environ['TMP']+"/NumPol_"+NumPol+".shp", "utf-8", None, "ESRI Shapefile")
                    vlayer = QgsVectorLayer(os.environ['TMP']+"/NumPol_"+NumPol+".shp", titol3.decode('utf8'), "ogr")
                    symbols=vlayer.rendererV2().symbols()
                    symbol=symbols[0]
                    symbol.setColor(self.dlg.ColorTopos.palette().color(1))
                    QgsMapLayerRegistry.instance().addMapLayer(vlayer,False)
                    root = QgsProject.instance().layerTreeRoot()
                    myLayerNode=QgsLayerTreeLayer(vlayer)
                    root.insertChildNode(0,myLayerNode)
                    myLayerNode.setCustomProperty("showFeatureCount", True)
                    
                    qgis.utils.iface.mapCanvas().refresh()
                    qgis.utils.iface.legendInterface().refreshLayerSymbology(vlayer)

                else:
                    QMessageBox.information(None, "LAYER ERROR 0:", "%s\n\nThe layer %s is not valid" % ("error","nom_layer"))

                if (self.dlg.topo.isChecked()): #Calcul mitjançant numero de policia
                    if (self.dlg.ZIGraf_radio.isChecked()):
                        
                        #Calcul mitjançant GRAF
                        #print sql_total
                        progress.setValue(30)

                        self.dlg.Progres.setValue(30)
                        qApp.processEvents()
#                       *****************************************************************************************************************
#                       INICI CALCUL DEL GRAF I DEL BUFFER DELS TRAMS CALCULATS 
#                       *****************************************************************************************************************
                        sql_buffer=self.calcul_graf(sql_total)
#                       *****************************************************************************************************************
#                       FI CALCUL DEL GRAF I DEL BUFFER DELS TRAMS CALCULATS 
#                       *****************************************************************************************************************
                        progress.setValue(60)
                        self.dlg.Progres.setValue(60)
                        qApp.processEvents()
                        sql_ZI=sql_buffer #"select TOT.\"EPIGRAFIAE\",TOT.\"Carrer_Num_Bis\",TOT.\"REF_CADAST\",TOT.\"NumPol\",TOT.\"METRES2\",TOT.\"radi\",row_number() OVER () AS \"ogc_fid\",ST_Buffer(TOT.\"geom\","+self.dlg.Radi_ZI.text()+"::double precision) AS the_geom from ("+sql_buffer+") TOT"
                        #sql_PART1_ZI="SELECT row_number() OVER () AS \"ogc_fid\",ILL.\"D_S_I\",ILL.\"geom\",RS.\"Habitants\" as hab FROM (select \"ILLES\".\"D_S_I\",\"ILLES\".\"geom\" from \"ILLES\" where \"ILLES\".\"id\" NOT IN (select \"ILLES\".\"id\" from \"ILLES\" INNER JOIN ("
                        sql_PART1_ZI="SELECT row_number() OVER () AS \"id\",ILL.\"geom\",RS.\"Habitants\" as hab FROM (select \"ILLES\".\"D_S_I\",\"ILLES\".\"geom\" from \"ILLES\" where \"ILLES\".\"id\" NOT IN (select \"ILLES\".\"id\" from \"ILLES\" INNER JOIN ("
                        #print "buf:"+sql_buffer
                        #print "ZI:"+sql_ZI
                        #print "PART1_ZI:"+sql_PART1_ZI
                        
                        sql_TOTAL_ZI=sql_PART1_ZI+sql_ZI+") TOT2 on ST_Intersects(\"ILLES\".\"geom\",TOT2.\"the_geom\"))) ILL JOIN \"Resum_Temp_"+Fitxer+"\" RS on (ILL.\"D_S_I\" = RS.\"ILLES_Codificades\")"
                    else:
                        
                        #Calcul mitjançant Zona Circular
                        sql="SELECT BC.\"EPIGRAFIAE\",DI.\"Carrer_Num_Bis\",DI.\"REF_CADAST\",DI.\"geom\",BC.\"NumPol\",BC.\"METRES2\",("+self.dlg.texte_2.text()+"*SQRT(BC.\"METRES2\"/ PI())) AS RADI FROM (select * from \"BrossaComercial\" "
                        wheresql="where \"EPIGRAFIAE\" in "+where_sentence+") BC LEFT JOIN \"dintreilla\" DI ON (BC.\"NumPol\" = DI.\"Carrer_Num_Bis\")"
                        sql_ZI="select TOT.\"EPIGRAFIAE\",TOT.\"Carrer_Num_Bis\",TOT.\"REF_CADAST\",TOT.\"NumPol\",TOT.\"METRES2\",TOT.\"radi\",row_number() OVER () AS \"ogc_fid\",ST_Buffer(TOT.\"geom\","+self.dlg.Radi_ZI.text()+"::double precision) AS the_geom from ("+sql+wheresql+") TOT"
                        sql_PART1_ZI="SELECT row_number() OVER () AS \"ogc_fid\",ILL.\"D_S_I\",ILL.\"geom\",RS.\"Habitants\" FROM (select \"ILLES\".\"D_S_I\",\"ILLES\".\"geom\" from \"ILLES\" where \"ILLES\".\"id\" NOT IN (select \"ILLES\".\"id\" from \"ILLES\" INNER JOIN ("
                        sql_TOTAL_ZI=sql_PART1_ZI+sql_ZI+") TOT2 on ST_Intersects(\"ILLES\".\"geom\",TOT2.\"the_geom\"))) ILL JOIN \"Resum_Temp_"+Fitxer+"\" RS on (ILL.\"D_S_I\" = RS.\"ILLES_Codificades\")"
                else:

                    #Calcul mitjançant parceles
               
                    sql="SELECT PA.\"geom\",PACOUNT.\"numae\",PA.\"UTM\" FROM (SELECT count(BC.\"EPIGRAFIAE\") as numAE , PA.\"UTM\" FROM (select * from \"BrossaComercial\" where \"EPIGRAFIAE\" in "+where_sentence+") BC LEFT JOIN \"parcel\" PA ON (BC.\"CADASREF\" = PA.\"UTM\") WHERE (PA.\"UTM\" IS NOT NULL) AND (PA.\"UTM\"<>' ')  GROUP BY PA.\"UTM\") PACOUNT LEFT JOIN \"parcel\" PA ON (PACOUNT.\"UTM\"=PA.\"UTM\") WHERE (PACOUNT.\"numae\">0) "
                    sql_ZI="select TOT.\"UTM\",TOT.\"numae\",row_number() OVER () AS \"ogc_fid\",ST_Buffer(TOT.\"geom\","+self.dlg.Radi_ZI.text()+"::double precision) as the_geom from ("+sql+") TOT"
                    sql_PART1_ZI="SELECT ILL.\"D_S_I\",ILL.\"geom\",RS.\"Habitants\" FROM (select \"ILLES\".\"D_S_I\",\"ILLES\".\"geom\" from \"ILLES\" where \"ILLES\".\"id\" NOT IN (select \"ILLES\".\"id\" from \"ILLES\" INNER JOIN ("
                    sql_TOTAL_ZI=sql_PART1_ZI+sql_ZI+") TOT2 on ST_Intersects(\"ILLES\".\"geom\",TOT2.\"the_geom\"))) ILL JOIN \"Resum_Temp_"+Fitxer+"\" RS on (ILL.\"D_S_I\" = RS.\"ILLES_Codificades\")"
                
                uri.setDataSource("","("+sql_TOTAL_ZI+")","geom","","id")
                if (self.dlg.RelacionarPoblacio.isChecked()):
                    titol=self.dlg.texte_3.text().replace("'","\'")

                    if Auto_generacio==False:
                        if (self.dlg.GrafCombo.currentText()=="Distancia" or self.dlg.ZICirc_radio.isChecked()):
                            titol2=u'Temàtic de població que es troba a més de '+self.dlg.Radi_ZI.text()+u' m de la activitat '
                        else:
                            titol2=u'Temàtic de població que es troba a més de '+self.dlg.Radi_ZI.text()+u' min de la activitat '
                        titol3=titol2.encode('utf8','strict')+titol.encode('utf8','strict')
                    else:
                        if (self.dlg.GrafCombo.currentText()=="Distancia" or self.dlg.ZICirc_radio.isChecked()):
                            titol2=self.dlg.Radi_ZI.text().encode('utf8','strict')
                            titol3=titol.encode('utf8','strict')+"_"+titol2.encode('utf8','strict')+u'm_PE'
                        else:
                            titol3=titol.encode('utf8','strict')+"_"+self.dlg.Radi_ZI.text()+u'min_PE'                            
                        cur.execute("DROP TABLE IF EXISTS \""+titol3+"\";")
                        conn.commit()
                        cur.execute("CREATE TABLE \""+titol3+"\" AS ("+sql_TOTAL_ZI+");")
                        conn.commit()
                        #ALTER TABLE IF EXISTS "public"."Farmacies_300m_ZI" ALTER COLUMN geom TYPE geometry(Multipolygon,25831) USING ST_Multi(geom);
                        cur.execute("ALTER TABLE IF EXISTS \"public\".\""+titol3+"\" ALTER COLUMN geom TYPE geometry(Multipolygon,25831) USING ST_Multi(geom);")
                        conn.commit()
                        #cur.execute("COMMENT ON TABLE \""+titol3+"\" IS '"+titol3+" "+datetime.datetime.now().strftime("%B %Y")+"';")
                        cur.execute("COMMENT ON TABLE \""+titol3+"\" IS '"+titol3+" "+mes[date.today().month]+" "+str(date.today().year)+"';")
                        conn.commit()                            

                        
                    vlayer = QgsVectorLayer(uri.uri(), titol3.decode('utf8'), "postgres")
                    if vlayer.isValid():
                        Tematic=datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                        error=QgsVectorFileWriter.writeAsVectorFormat(vlayer, os.environ['TMP']+"/Tematic_"+Tematic+".shp", "utf-8", None, "ESRI Shapefile")
                        vlayer = QgsVectorLayer(os.environ['TMP']+"/Tematic_"+Tematic+".shp", titol3.decode('utf8'), "ogr")
                        cur.execute("DROP TABLE IF EXISTS \"Resum_Temp_"+Fitxer+"\"")
                        conn.commit()
                        fieldname="Habitants"
                        numberOfClasses=5
                        myRangeList=[]
                        mysymbol=QgsFillSymbolV2()
                        if (self.dlg.ColorDegradat.currentText()=='Gris'):
                            colorRamp=QgsVectorGradientColorRampV2( QColor( 230, 230, 230 ), QColor( 60, 60, 60 ))
                        elif (self.dlg.ColorDegradat.currentText()=='Vermell'):
                            colorRamp=QgsVectorGradientColorRampV2( QColor( 255, 154, 154 ), QColor( 154, 0, 0 ))
                        elif (self.dlg.ColorDegradat.currentText()=='Groc'):
                            colorRamp=QgsVectorGradientColorRampV2( QColor( 255, 255, 154 ), QColor( 154, 154, 0 ))
                        elif (self.dlg.ColorDegradat.currentText()=='Blau'):
                            colorRamp=QgsVectorGradientColorRampV2( QColor( 154, 255, 255 ), QColor( 0, 0, 154 ))
                        elif (self.dlg.ColorDegradat.currentText()=='Verd'):
                            colorRamp=QgsVectorGradientColorRampV2( QColor( 154, 255, 154 ), QColor( 0, 154, 0 ))
                        
                        format = QgsRendererRangeV2LabelFormat()
                        template = "%1 - %2 habitants"
                        precision = 0
                        format.setFormat(template)
                        format.setPrecision(precision)
                        format.setTrimTrailingZeroes(True)
                        renderer=QgsGraduatedSymbolRendererV2.createRenderer(vlayer,fieldname,numberOfClasses,QgsGraduatedSymbolRendererV2.Quantile,mysymbol,colorRamp)
                        renderer.setLabelFormat(format,True)
                        vlayer.setRendererV2(renderer)
                        
                        QgsMapLayerRegistry.instance().addMapLayer(vlayer,False)
                        root = QgsProject.instance().layerTreeRoot()
                        myLayerNode=QgsLayerTreeLayer(vlayer)
                        root.insertChildNode(0,myLayerNode)
                        myLayerNode.setCustomProperty("showFeatureCount", True)
                        qgis.utils.iface.mapCanvas().refresh()
                        qgis.utils.iface.legendInterface().refreshLayerSymbology(vlayer)
                    else:
                        QMessageBox.information(None, "LAYER ERROR 1:", "%s\n\nThe layer %s is not valid" % ("error","nom_layer"))
                progress.setValue(70)
                self.dlg.Progres.setValue(70)
                qApp.processEvents()

                if (self.dlg.Veure_ZI.isChecked()):
                    if not(self.dlg.NoMostrarZI.isChecked()):
                        if self.dlg.topo.isChecked():
                            if (self.dlg.ZIGraf_radio.isChecked()):
                                #sql_total1="SELECT row_number() OVER () AS \"ogc_fid\",\"punt_id\",\"the_geom\" FROM Buffer_Final_"+Fitxer
                                sql_total1="SELECT row_number() OVER () AS \"id\",\"the_geom\" as \"geom\" FROM Buffer_Final_"+Fitxer
                                
                            else:
                                sql1="SELECT BC.\"EPIGRAFIAE\",DI.\"Carrer_Num_Bis\",DI.\"REF_CADAST\",DI.\"geom\",BC.\"NumPol\",BC.\"METRES2\",("+self.dlg.texte_2.text()+"*SQRT(BC.\"METRES2\"/ PI())) AS RADI FROM (select * from \"BrossaComercial\" "
                                wheresql1="where \"EPIGRAFIAE\" in "+where_sentence+") BC LEFT JOIN \"dintreilla\" DI ON (BC.\"NumPol\" = DI.\"Carrer_Num_Bis\")"
                                sql_total1="select TOT.\"EPIGRAFIAE\",TOT.\"Carrer_Num_Bis\",TOT.\"REF_CADAST\",TOT.\"NumPol\",TOT.\"METRES2\",TOT.\"radi\",row_number() OVER () AS \"ogc_fid\",ST_Buffer(TOT.\"geom\","+self.dlg.Radi_ZI.text()+"::double precision) AS geom from ("+sql+wheresql+") TOT"
                        else:
                            sql="SELECT PA.\"geom\",PACOUNT.\"numae\",PA.\"UTM\" FROM (SELECT count(BC.\"EPIGRAFIAE\") as numAE , PA.\"UTM\" FROM (select * from \"BrossaComercial\" where \"EPIGRAFIAE\" in "+where_sentence+") BC LEFT JOIN \"parcel\" PA ON (BC.\"CADASREF\" = PA.\"UTM\") WHERE (PA.\"UTM\" IS NOT NULL) AND (PA.\"UTM\"<>' ')  GROUP BY PA.\"UTM\") PACOUNT LEFT JOIN \"parcel\" PA ON (PACOUNT.\"UTM\"=PA.\"UTM\") WHERE (PACOUNT.\"numae\">0) "
                            sql_total1="select TOT.\"UTM\" as \"ogc_fid\",TOT.\"numae\",ST_Buffer(TOT.\"geom\","+self.dlg.Radi_ZI.text()+"::double precision) as geom from ("+sql+") TOT"
                            
                        uri.setDataSource("","("+sql_total1+")","geom","","id")
                        titol=self.dlg.texte_3.text().replace("'","\'")
                        if Auto_generacio==False:
                            titol2=u'Àrea influència dels números de policia amb activitat: '
                            titol3=titol2.encode('utf8','strict')+titol.encode('utf8','strict')
                        else:
                            if (self.dlg.GrafCombo.currentText()=="Distancia" or self.dlg.ZICirc_radio.isChecked()):
                                titol2=self.dlg.Radi_ZI.text().encode('utf8','strict')
                                titol3=titol.encode('utf8','strict')+"_"+titol2.encode('utf8','strict')+u'm_ZI'
                            else:
                                titol3=titol.encode('utf8','strict')+"_"+self.dlg.Radi_ZI.text()+u'min_ZI'                            
                            cur.execute("DROP TABLE IF EXISTS \""+titol3+"\";")
                            conn.commit()
                            cur.execute("CREATE TABLE \""+titol3+"\" AS ("+sql_total1+");")
                            conn.commit()                            
                            cur.execute("COMMENT ON TABLE \""+titol3+"\" IS '"+titol3+" "+mes[date.today().month]+" "+str(date.today().year)+"';")
                            conn.commit()                            
                        vlayer = QgsVectorLayer(uri.uri(), titol3.decode('utf8'), "postgres")
                        if vlayer.isValid():
                            Area=datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                            error=QgsVectorFileWriter.writeAsVectorFormat(vlayer, os.environ['TMP']+"/Area_"+Area+".shp", "utf-8", None, "ESRI Shapefile")
                            vlayer=None
                            vlayer = QgsVectorLayer(os.environ['TMP']+"/Area_"+Area+".shp", titol3.decode('utf8'), "ogr")
                            cur.execute("DROP TABLE IF EXISTS Buffer_Final_"+Fitxer)
                            conn.commit()
                            symbols = vlayer.rendererV2().symbols()
                            symbol=symbols[0]
                            symbol.setColor(self.dlg.ColorZI.palette().color(1))
                            vlayer.setLayerTransparency(self.dlg.Transparencia.value())
                            QgsMapLayerRegistry.instance().addMapLayer(vlayer,False)
                            root = QgsProject.instance().layerTreeRoot()
                            myLayerNode=QgsLayerTreeLayer(vlayer)
                            root.insertChildNode(0,myLayerNode)
                            myLayerNode.setCustomProperty("showFeatureCount", True)
                            qgis.utils.iface.mapCanvas().refresh()
                            qgis.utils.iface.legendInterface().refreshLayerSymbology(vlayer)
                        else:
                            QMessageBox.information(None, "LAYER ERROR 2:", "%s\n\nThe layer %s is not valid" % ("error","nom_layer"))
                    progress.setValue(90)
                    self.dlg.Progres.setValue(90)
                    qApp.processEvents()
                    
                    if (self.dlg.MostrarGraf_chk.isChecked()):
                        uri.setDataSource("","(SELECT * FROM Graf_utilitzat_"+Fitxer+")","the_geom","","punt_id")
                        titol=self.dlg.texte_3.text().replace("'","\'")
                        titol2=u'Graf: '
                        titol3=titol2.encode('utf8','strict')+titol.encode('utf8','strict')
                        vlayer = QgsVectorLayer(uri.uri(), titol3.decode('utf8'), "postgres")
                        if vlayer.isValid():
                            Graf=datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                            error=QgsVectorFileWriter.writeAsVectorFormat(vlayer, os.environ['TMP']+"/Graf_"+Graf+".shp", "utf-8", None, "ESRI Shapefile")
                            vlayer = QgsVectorLayer(os.environ['TMP']+"/Graf_"+Graf+".shp", titol3.decode('utf8'), "ogr")
                            cur.execute("DROP TABLE IF EXISTS Graf_utilitzat_"+Fitxer)
                            conn.commit()

                            symbols = vlayer.rendererV2().symbols()
                            symbol=symbols[0]
                            symbol.setColor(self.dlg.ColorGraf.palette().color(1))
                            vlayer.setLayerTransparency(self.dlg.Transparencia.value())
                            QgsMapLayerRegistry.instance().addMapLayer(vlayer,False)
                            root = QgsProject.instance().layerTreeRoot()
                            myLayerNode=QgsLayerTreeLayer(vlayer)
                            root.insertChildNode(0,myLayerNode)
                            myLayerNode.setCustomProperty("showFeatureCount", True)
                            qgis.utils.iface.mapCanvas().refresh()
                            qgis.utils.iface.legendInterface().refreshLayerSymbology(vlayer)
                        else:
                            QMessageBox.information(None, "LAYER ERROR 3:", "%s\n\nThe layer %s is not valid" % ("error","nom_layer"))
                progress.setValue(0)
                self.bar.setEnabled(True)
                self.dlg.Progres.setValue(0)
                self.dlg.Progres.setVisible(False)
                self.bar.clearWidgets()
                self.dlg.EstatConnexioFixa.setText(u'Estat de la connexió:')
                qApp.processEvents()

            else:
                QMessageBox.information(None, u'Informació:', u'No hi ha cap element seleccionat')
        else:
            QMessageBox.information(None, u'Informació:', u'No està connectat a cap base de dades')

        print "Durada: "+str(int(time.time()-a))+" s."
        nom_conn=self.dlg.ComboConn.currentText()
        select = u'Selecciona connexió'
        if nom_conn==select:
            self.dlg.EstatConnexio.setText(u'No connectat')
            self.dlg.EstatConnexio.setStyleSheet('border:1px solid #000000; background-color: #FFFFFF')
        else:
            self.dlg.EstatConnexio.setText(u'Connectat')
            self.dlg.EstatConnexio.setStyleSheet('border:1px solid #000000; background-color: #7fff7f')
        self.dlg.Progres.setVisible(False)
        self.bar.clearWidgets()
        self.dlg.Progres.setVisible(False)
        qApp.processEvents()

    #@pyqtSlot()

    def on_click_Sortir(self):
        """Aquesta funcio tanca el plugin"""
        self.EstatInicial()
        self.dlg.close()

    def on_click_AutoGenera(self):
        global Auto_generacio
        global Auto_primera_vegada
        Auto_generacio=True
        Auto_primera_vegada=True
        self.dlg.Veure_ZI.setChecked(True)
        self.dlg.ZIGraf_radio.setChecked(True)
        self.dlg.RelacionarPoblacio.setChecked(True)
        self.dlg.Radi_ZI.setText(u'150')
        qApp.processEvents()
        self.on_click_INICI()
        self.dlg.Radi_ZI.setText(u'300')
        qApp.processEvents()
        self.on_click_INICI()
        self.dlg.GrafCombo.setCurrentIndex(1)
        self.dlg.CostInvers_chk.setChecked(True)
        self.dlg.CostNusos.setChecked(True)
        self.dlg.Radi_ZI.setText(u'2')
        qApp.processEvents()
        self.on_click_INICI()
        self.dlg.Radi_ZI.setText(u'3')
        qApp.processEvents()
        self.on_click_INICI()
        self.dlg.Radi_ZI.setText(u'5')
        qApp.processEvents()
        self.on_click_INICI()
        Auto_generacio=False

    def campGeometria(self, taula):
        '''Aquesta funció retorna el camp de geometria de la taula que li passem per parametres'''
        global cur
        global conn
        sql = "select f_geometry_column from geometry_columns where f_table_name = '" + taula + "'"
        #Connexio
        cur.execute(sql)
        camp = cur.fetchall()
               
        return camp[0][0]

    def on_Change_ComboConn(self):
        """Aquesta funcio fa els passos necssaris per connectar-se a la BD indicada per l'usuari"""
        global nomBD1
        global contra1
        global host1
        global port1
        global usuari1
        global schema
        global cur
        global conn
        s = QSettings()
        nom_conn=self.dlg.ComboConn.currentText()
        select = u'Selecciona connexió'
        if nom_conn != select:
            s.beginGroup("PostgreSQL/connections/"+nom_conn)
            currentKeys = s.childKeys()
            
            nomBD1 = s.value("database", "" )
            contra1 = s.value("password", "" )
            host1 = s.value("host", "" )
            port1 = s.value("port", "" )
            usuari1 = s.value("username", "" )
            schema= 'public'
            #Connexio
            nomBD = nomBD1.encode('ascii','ignore')
            usuari = usuari1.encode('ascii','ignore')
            servidor = host1.encode('ascii','ignore')     
            contrasenya = contra1.encode('ascii','ignore')
            self.dlg.barraCerca.clear()
            
            self.dlg.ListaActivitatsDesc.clear()
            self.dlg.ListaActivitatsEpigraf.clear()
            self.dlg.EstatConnexio.setStyleSheet('border:1px solid #000000; background-color: #ffff7f')
            self.dlg.EstatConnexio.setText(u'Connectant...')
            self.dlg.EstatConnexio.setAutoFillBackground(True)
            qApp.processEvents()
    
            try:
                estructura = "dbname='"+ nomBD + "' user='" + usuari +"' host='" + servidor +"' password='" + contrasenya + "'"
                conn = psycopg2.connect(estructura)
                self.dlg.EstatConnexio.setStyleSheet('border:1px solid #000000; background-color: #7fff7f')
                self.dlg.EstatConnexio.setText(u'Connectat')
                cur = conn.cursor()
                self.cercaDescripcio()
                self.cercaEpigraf()
                
            except:
                self.dlg.ComboConn.setCurrentIndex(0)
                self.dlg.EstatConnexio.setStyleSheet('border:1px solid #000000; background-color: #ff7f7f')
                self.dlg.EstatConnexio.setText(u'Error: Problema en la connexió.')

                print "I am unable to connect to the database"
            
        else:
            self.dlg.EstatConnexio.setText(u'No connectat')
            self.dlg.EstatConnexio.setStyleSheet('border:1px solid #000000; background-color: #FFFFFF')
            self.dlg.ListaActivitatsDesc.clear()
            self.dlg.ListaActivitatsEpigraf.clear()
 
    def run(self):
        """Aquesta funcio executa el plugin"""
        conn=self.getConnections()
        self.EstatInicial()
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        layers = QgsMapLayerRegistry.instance().mapLayers().values()
        self.populateComboBox(self.dlg.ComboConn ,conn,u'Selecciona connexió',True)
        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
