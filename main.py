# pip install geopandas folium PyQt5 flask 
# pip install PyQtWebEngine
# pip install pyarrow
# pip install matplotlib mapclassify

import os, posixpath
import sys

from flask import Flask, request, jsonify
import sqlite3

import pandas as pd
import geopandas as gpd
import numpy as np
# import matplotlib.pyplot as plt
# import duckdb

import folium

from PyQt5.QtCore import QThread, QUrl, Qt #, QTimer, QRect, QPoint, QEvent,
from PyQt5.QtGui import QCursor #QPalette, , QRegion, QPainter
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QRadioButton, \
    QWidget, QHBoxLayout, QVBoxLayout, QMenu, \
    QSizePolicy, QStyle, QStyleOption, QStyleHintReturnMask, \
    QLabel, QPushButton, QFrame, QLineEdit, QTableWidget, \
    QGroupBox, QListWidget, QComboBox, QProgressBar



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__kpi_selected = 'hr'
        self.__reg_selected = ''


        self.__cd = os.getcwd()
        self.__data = gpd.read_parquet(resource_path('data/gdf_novos_por_regiao.parquet'))
        self.__data['municipio'] = self.__data['cd_RegiaoRisco'].astype(str).str[:7]
        self.__data['uf'] = self.__data['cd_RegiaoRisco'].astype(str).str[:2]
        self.__data['macrorregiao'] = self.__data['cd_RegiaoRisco'].astype(str).str[:1]

        self.__initUi()

    def __initUi(self):
        self.setWindowTitle('Z Maps')

        
        self.__view = QWebEngineView()




        lay = QVBoxLayout()
        lay.addWidget(self.__view)

        leftWidget = QWidget()
        leftWidget.setLayout(lay)





        hr_MarkerRadBtn = QRadioButton('Hit Ratio')
        hr_MarkerRadBtn.setChecked(True)
        hr_MarkerRadBtn.clicked.connect(lambda x: self.__select_kpi('hr'))


        lr_MarkerRadBtn = QRadioButton('Loss wo Ulae')
        lr_MarkerRadBtn.clicked.connect(lambda x: self.__select_kpi('lr'))



        lay = QVBoxLayout()
        lay.addWidget(hr_MarkerRadBtn)
        lay.addWidget(lr_MarkerRadBtn)

        kpi_OptionGrpBox = QGroupBox()
        kpi_OptionGrpBox.setTitle('KPI mostrado')
        kpi_OptionGrpBox.setLayout(lay)

        
        # kpi_OptionGrpBox.selectionChanged.connect(self.__selectionChanged)




        lista_regioes = QComboBox()
        lista_regioes.addItem('')
        lista_regioes.addItem('3550308')
        lista_regioes.addItem('2927408')
        lista_regioes.addItem('3106200')
        lista_regioes.currentTextChanged.connect(lambda x: self.__btn_load_regiao.setEnabled(True) if lista_regioes.currentText() != self.__reg_selected else self.__btn_load_regiao.setEnabled(False))


        self.__btn_load_regiao = QPushButton('Carregar Regiao')
        self.__btn_load_regiao.setCursor(QCursor(Qt.PointingHandCursor))
        self.__btn_load_regiao.clicked.connect(lambda x: self.__load_regiao(lista_regioes.currentText()))



        self.__statusLabel = QLabel('Nenhum mapa carregado')
        self.__progressBar = QProgressBar()
        self.__progressBar.setMinimum(0)
        self.__progressBar.setMaximum(100)
        self.__progressBar.setValue(0)
        


        def create_sep():
            sep = QFrame()
            sep.setFrameShape(QFrame.HLine)
            sep.setFrameShadow(QFrame.Sunken)
            return sep

        # sep = QFrame()
        # sep.setFrameShape(QFrame.HLine)
        # sep.setFrameShadow(QFrame.Sunken)

        # routeLineEdit = QLineEdit()

        # addRouteBtn = QPushButton('Add')
        # addRouteBtn.setCursor(QCursor(Qt.PointingHandCursor))

        # addRouteBtn.clicked.connect(self.__addMark)

        # delRouteBtn = QPushButton('Delete')
        # connectBtn = QPushButton('Polygon')

        # lay = QHBoxLayout()
        # lay.addWidget(addRouteBtn)
        # lay.addWidget(delRouteBtn)
        # lay.addWidget(connectBtn)
        # lay.setContentsMargins(0, 0, 0, 0)

        # routeBtnWidget = QWidget()
        # routeBtnWidget.setLayout(lay)

        # tableWidget = QTableWidget()

        lay = QVBoxLayout()
        lay.addWidget(create_sep())
        lay.addWidget(lista_regioes)
        lay.addWidget(self.__btn_load_regiao)
        lay.addWidget(create_sep())
        lay.addWidget(self.__statusLabel)
        lay.addWidget(self.__progressBar)
        lay.addWidget(create_sep())
        lay.addWidget(kpi_OptionGrpBox)
        lay.addWidget(create_sep())
        # lay.addWidget(QLabel('Name of Route'))
        # lay.addWidget(routeLineEdit)
        # lay.addWidget(routeBtnWidget)
        # lay.addWidget(tableWidget)
        lay.setAlignment(Qt.AlignTop)
        lay.setContentsMargins(0, 0, 0, 0)


        controlWidget = QWidget()
        controlWidget.setLayout(lay)
        controlWidget.setFixedWidth(250)


        lay = QHBoxLayout()
        lay.addWidget(leftWidget)
        lay.addWidget(controlWidget)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.__load_regiao('')  
        self.setCentralWidget(mainWidget)
        self.showMaximized()




    # def keyPressEvent(self, e):
    #     if e.key() == Qt.Key_F11:
    #         self.showFullScreen()
    #     elif e.key() == Qt.Key_Escape:
    #         if self.isFullScreen():
    #             self.showNormal()
    #     return super().keyPressEvent(e)

    def __select_kpi(self, text):
        self.__kpi_selected = text

        if self.__reg_selected != '':
            self.__reload_mapa()



    def __load_regiao(self, regiao):
        if regiao == '':
            # map_filename = os.path.join(self.__cd, f'map_start.html').replace(os.path.sep, posixpath.sep)
            map_filename = resource_path('map_start.html')
            self.__view.load(QUrl.fromLocalFile(map_filename))
            self.__statusLabel.setText(f'Nenhuma região selecionada')
            self.__progressBar.setValue(100)

        else:
            
            self.__statusLabel.setText(f'Filtrando arquivos...')
            self.__progressBar.setValue(0)

            df_flt = self.__data[self.__data['municipio'] == regiao]

            for i in range(20):
                self.__progressBar.setValue(i)


            self.__statusLabel.setText(f'Criando mapa HR...')

            df_flt.explore(tiles = 'cartodb positron', 
                                    column = 'hr',
                                    cmap = 'coolwarm',).save('mapa_hr.html')


            for i in range(20, 60):
                self.__progressBar.setValue(i)


            self.__statusLabel.setText(f'Criando mapa LR...')

            df_flt.explore(tiles = 'cartodb positron', 
                                    column = 'Loss_Obs_wo_ulae',
                                    cmap = 'coolwarm',).save('mapa_lr.html')

            for i in range(60, 100):
                self.__progressBar.setValue(i)

            self.__statusLabel.setText(f'Mapas da regiao {regiao} prontos!')

            self.__reload_mapa()



            # map_filename = os.path.join(self.__cd, f'mapa_{self.__kpi_selected}.html').replace(os.path.sep, posixpath.sep)
            # self.__view.load(QUrl.fromLocalFile(map_filename))
        
        # self.__view.selectionChanged.connect(self.__selectionChanged)
        
        self.__reg_selected = regiao
        self.__btn_load_regiao.setEnabled(False)


    def __reload_mapa(self):
        # map_filename = os.path.join(self.__cd, f'mapa_{self.__kpi_selected}.html').replace(os.path.sep, posixpath.sep)
        map_filename = resource_path(f'mapa_{self.__kpi_selected}.html')
        self.__view.load(QUrl.fromLocalFile(map_filename))





class FlaskThread(QThread):

    def __init__(self, application):
        QThread.__init__(self)
        self.application = application

    def __del__(self):
        self.wait()

    def run(self):
        self.application.run(port=5000)



def start_app_qt(application):
    qtapp = QApplication(sys.argv)

    webapp = FlaskThread(application)
    webapp.start()

    qtapp.aboutToQuit.connect(webapp.terminate)

    w = MainWindow()
    w.show()

    return qtapp.exec()



if __name__ == "__main__":

    app = Flask(__name__)

    @app.route('/add_marker', methods=['POST'])
    def add_marker():
        try:
            # Get the marker data from the request body
            data = request.get_json()
            print('saved in server-side')

            # Save the marker data to the SQLite3 database file
            conn = sqlite3.connect('markers.db')
            c = conn.cursor()
            c.execute('INSERT INTO markers (lat, lng) VALUES (?, ?)', (data['lat'], data['lng']))
            conn.commit()
            conn.close()

            # Do something with the lat and lng values, like adding them to a 
            # database
            return jsonify({'status': 'ok'})
        except Exception as e:
            print(e)
            raise Exception



    sys.exit(start_app_qt(app))

