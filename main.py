# pip install geopandas folium PyQt5 flask 
# pip install PyQtWebEngine
# pip install pyarrow
# pip install matplotlib mapclassify

import os, posixpath
import sys

# from flask import Flask, request, jsonify
# import sqlite3

import pandas as pd
from pandas._libs.lib import is_integer

import geopandas as gpd
import numpy as np

import branca.colormap as cm



from PyQt5.QtCore import QThread, QUrl, Qt #, QTimer, QRect, QPoint, QEvent,
from PyQt5.QtGui import QCursor #QPalette, , QRegion, QPainter
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile

from PyQt5.QtWidgets import QApplication, QMainWindow, QRadioButton, \
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, \
    QGroupBox, QComboBox, QProgressBar
    # QMenu, QLineEdit, QTableWidget, QListWidget,  \
    # QSizePolicy, QStyle, QStyleOption, QStyleHintReturnMask, \



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
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

        self.__data['regiao'] = np.where(self.__data['uf'] == '35', 'SP', 
                                np.where(self.__data['uf'] == '33', 'RJ',
                                np.where(self.__data['uf'] == '31', 'MG',
                                np.where(self.__data['uf'] == '32', 'ES',
                                np.where(self.__data['uf'] == '41', 'PR',
                                np.where(self.__data['uf'] == '42', 'SC',
                                np.where(self.__data['uf'] == '43', 'RS',
                                np.where(self.__data['uf'] == '50', 'MT',
                                np.where(self.__data['uf'] == '51', 'MS',
                                np.where(self.__data['uf'] == '52', 'GO',
                                np.where(self.__data['uf'] == '53', 'DF',
                                np.where(self.__data['macrorregiao'] == '2', 'NE', 'NO'
                                        ))))))))))))
        

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

        

        lista_regioes = QComboBox()
        lista_regioes.addItem('')
        lista_regioes.addItem('SP')
        lista_regioes.addItem('MG')
        lista_regioes.addItem('ES')
        lista_regioes.addItem('RJ')
        lista_regioes.addItem('GO')
        lista_regioes.addItem('DF')
        lista_regioes.addItem('MS')
        lista_regioes.addItem('MT')
        lista_regioes.addItem('PR')
        lista_regioes.addItem('SC')
        lista_regioes.addItem('RS')
        lista_regioes.addItem('NE')
        lista_regioes.addItem('NO')
        lista_regioes.setStyleSheet(
            """
            font-size: 15px;
            """
        )


        lista_regioes.currentTextChanged.connect(lambda x: self.__btn_load_regiao.setEnabled(True) if lista_regioes.currentText() != self.__reg_selected else self.__btn_load_regiao.setEnabled(False))


        self.__btn_load_regiao = QPushButton('Carregar Regiao')
        self.__btn_load_regiao.setCursor(QCursor(Qt.PointingHandCursor))
        self.__btn_load_regiao.clicked.connect(lambda x: self.__load_regiao(lista_regioes.currentText()))
        self.__btn_load_regiao.setStyleSheet(
            """
            font-size: 13px;
            """
        )


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



    def __criar_color_map(self, positivo = True, indices = [0, 0.2, 0.3, 0.5, 0.7, 0.8, 1.]):
        q0, q10 = indices[0], indices[-1]
        n0, n2, n3, n5, n7, n8, n10 = [(j - q0)/(q10 - q0) for j in indices]

        if positivo:
            return cm.LinearColormap(
                [(0.6980392156862745, 0.09411764705882353, 0.16862745098039217, 1.0),
                (0.9372549019607843, 0.5411764705882353, 0.3843137254901961, 1.0),
                (0.9921568627450981, 0.8588235294117647, 0.7803921568627451, 1.0),
                # (0.8196078431372549, 0.8980392156862745, 0.9411764705882353, 1.0),
                (0.403921568627451, 0.6627450980392157, 0.8117647058823529, 1.0),
                (0.12941176470588237, 0.4, 0.6745098039215687, 1.0)], 

                # [0., 0.2, 0.5,  0.7, 1.],
                [n0, n2, n5, n7, n10],
                # [0., 0.2, 0.5,  0.7, 1.],
                max_labels = 0
                ).scale(q0, q10)
        
        else:
            return cm.LinearColormap(
                [(0.12941176470588237, 0.4, 0.6745098039215687, 1.0),
                (0.403921568627451, 0.6627450980392157, 0.8117647058823529, 1.0),
                # (0.8196078431372549, 0.8980392156862745, 0.9411764705882353, 1.0),
                (0.9921568627450981, 0.8588235294117647, 0.7803921568627451, 1.0),
                (0.9372549019607843, 0.5411764705882353, 0.3843137254901961, 1.0),
                (0.6980392156862745, 0.09411764705882353, 0.16862745098039217, 1.0)], 

                [n0, n3, n5, n8, n10],
                # [0., 0.3, 0.5, 0.8, 1.],
                max_labels = 0
                ).scale(q0, q10)
        

    def __weighted_qcut(self, values, weights, q, **kwargs):
        'Return weighted quantile cuts from a given series, values.'
        if is_integer(q):
            quantiles = np.linspace(0, 1, q + 1)
        else:
            quantiles = q
        order = weights.iloc[values.argsort()].cumsum()
        bins = pd.cut(order / order.iloc[-1], quantiles, **kwargs)

        return bins.sort_index()
    


    def __criar_mapas(self, dados, column, kpi):
        # define coluna peso para qebrar decis
        if kpi == 'hr':
            WEIGHT = 'n_calculos'
        elif kpi == 'lr':
            WEIGHT = 'Exposicao'
        
        # separa dados com e sem valores nulos
        dados_not_na = dados.dropna(subset = [column]).reset_index(drop = True)
        dados_na = dados[dados[column].isna()].reset_index(drop = True)


        # cria rank para os dados sem valores nulos
        COLUNA = f'rank_{kpi}'

        v0, v10 = dados_not_na[column].dropna().min(), dados_not_na[column].dropna().max()
        try:
            dados_not_na[COLUNA] = self.__weighted_qcut(dados_not_na[column], dados_not_na[WEIGHT], 10, labels = False)

            # calcula os representante de cada percentil
            valores = dados_not_na.groupby(COLUNA)[column].min()
            v2 = valores[2]
            v3 = valores[3]
            v5 = valores[5]
            v7 = valores[7]
            v8 = valores[8]

        except:
            dados_not_na[COLUNA] = self.__weighted_qcut(dados_not_na[column], dados_not_na[WEIGHT], 2, labels = False)

            # calcula os representante de cada percentil
            valores = dados_not_na.groupby(COLUNA)[column].min()
            v5 = valores[1]
            v2 = v0 + 0.4 * (v5 - v0)
            v3 = v0 + 0.6 * (v5 - v0)
            v7 = v5 + 0.4 * (v10 - v5)
            v8 = v5 + 0.6 * (v10 - v5)

        print(valores)
        
        # cria mapa de cores
        # minimo, maximo = dados_not_na[COLUNA].dropna().min(), dados_not_na[COLUMN].dropna().max()

        # print('*********** ' , column,  minimo, maximo)
        # print(dados.sort_values(column, ascending = False).head(1))

        if kpi == 'hr':
            color_map = self.__criar_color_map(positivo = True, indices = [v0, v2, v3, v5, v7, v8, v10])
        elif kpi == 'lr':
            color_map = self.__criar_color_map(positivo = False, indices = [v0, v2, v3, v5, v7, v8, v10])

        # color_map = color_map.scale(minimo, maximo)




        m = dados_not_na.explore(tiles = 'cartodb positron',
                                column = column,
                                cmap = color_map,)
        
        if dados_na.shape[0] > 0:
            m = dados_na.explore(m = m, color='black')
        
        m.save(f'mapa_{kpi}.html')

        return None




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

            df_flt = self.__data[self.__data['regiao'] == regiao]

            for i in range(20):
                self.__progressBar.setValue(i)


            self.__statusLabel.setText(f'Criando mapa HR...')

            self.__criar_mapas(df_flt, 'hr', 'hr')

            # df_flt.explore(tiles = 'cartodb positron', 
            #                         column = 'hr',
            #                         cmap = 'coolwarm',).save('mapa_hr.html')


            for i in range(20, 60):
                self.__progressBar.setValue(i)


            self.__statusLabel.setText(f'Criando mapa LR...')

            self.__criar_mapas(df_flt, 'Loss_Obs_wo_ulae', 'lr')


            # df_flt.explore(tiles = 'cartodb positron', 
            #                         column = 'Loss_Obs_wo_ulae',
            #                         cmap = 'coolwarm',).save('mapa_lr.html')

            for i in range(60, 101):
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





# class FlaskThread(QThread):

#     def __init__(self, application):
#         QThread.__init__(self)
#         self.application = application

#     def __del__(self):
#         self.wait()

#     def run(self):
#         self.application.run(port=5000)



# def start_app_qt(application):
def start_app_qt():
    qtapp = QApplication(sys.argv)

    # webapp = FlaskThread(application)
    # webapp.start()

    # qtapp.aboutToQuit.connect(webapp.terminate)

    w = MainWindow()
    w.show()

    return qtapp.exec()



if __name__ == "__main__":

    # app = Flask(__name__)

    # @app.route('/add_marker', methods=['POST'])
    # def add_marker():
    #     try:
    #         # Get the marker data from the request body
    #         data = request.get_json()
    #         print('saved in server-side')

    #         # Save the marker data to the SQLite3 database file
    #         conn = sqlite3.connect('markers.db')
    #         c = conn.cursor()
    #         c.execute('INSERT INTO markers (lat, lng) VALUES (?, ?)', (data['lat'], data['lng']))
    #         conn.commit()
    #         conn.close()

    #         # Do something with the lat and lng values, like adding them to a 
    #         # database
    #         return jsonify({'status': 'ok'})
    #     except Exception as e:
    #         print(e)
    #         raise Exception



    # sys.exit(start_app_qt(app))
    sys.exit(start_app_qt())

