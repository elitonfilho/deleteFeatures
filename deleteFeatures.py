# -*- coding: utf-8 -*-

import os

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.gui import *
from qgis.core import *
from deleteFeatures import resources



class DeleteFeatures:

    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        '''Start configurations'''
        self.initActions()
        self.initSignals()

    def initActions(self):
        self.coordinates = []
        self.toolbar = self.iface.addToolBar(
            "Delete Features by intersection")
        # Icons by FreePik and Kiranshastry
        icon_path = ':/plugins/deleteFeatures/filter_clipper.png'
        self.action_clipper = QAction(
            QIcon(icon_path), u"Remove feições realizando um clip", self.iface.mainWindow())
        self.action_clipper.setObjectName("Delete Features based on clip")
        self.action_clipper.setStatusTip(None)
        self.action_clipper.setWhatsThis(None)
        self.action_clipper.setCheckable(True)
        self.toolbar.addAction(self.action_clipper)

        icon_path = ':/plugins/deleteFeatures/filter_intersection.png'
        self.action_intersection = QAction(
            QIcon(icon_path), u"Remove feições realizando uma interseção", self.iface.mainWindow())
        self.action_intersection.setObjectName("Delete Features based on intersection")
        self.action_intersection.setStatusTip(None)
        self.action_intersection.setWhatsThis(None)
        self.action_intersection.setCheckable(True)
        self.toolbar.addAction(self.action_intersection)

        self.previousMapTool = self.iface.mapCanvas().mapTool()
        self.myMapTool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.isEditing = 0

    def initSignals(self):
        self.action_clipper.toggled.connect(self.RubberBand)
        self.action_clipper.toggled.connect(self.changeToClipper)
        self.action_intersection.toggled.connect(self.RubberBand)
        self.action_intersection.toggled.connect(self.changeToIntersection)
        self.myMapTool.canvasClicked.connect(self.mouseClick)

    def changeToClipper(self):
        self.currentTool = 'clipper'
        print(self.currentTool)

    def changeToIntersection(self):
        self.currentTool = 'intersection'
        print(self.currentTool)

    def disconnect(self):
        self.iface.mapCanvas().unsetMapTool(self.myMapTool)
        try:
            self.iface.mapCanvas().xyCoordinates.disconnect(self.mouseMove)
        except:
            pass

        try:
            self.myRubberBand.reset()
        except:
            pass

    def unChecked(self):
        self.action_clipper.setCheckable(False)
        self.action_clipper.setCheckable(True)

    def unload(self):
        self.disconnect()

    def RubberBand(self, boolean):
        if boolean:
            self.myRubberBand = QgsRubberBand(
                self.iface.mapCanvas(), QgsWkbTypes.PolygonGeometry)
            color = QColor(78, 97, 114)
            color.setAlpha(190)
            self.myRubberBand.setColor(color)
            self.myRubberBand.setFillColor(QColor(255, 0, 0, 40))
            #self.myRubberBand.setBorderColor(QColor(255, 0, 0, 200))

            # Set MapTool
            self.iface.mapCanvas().setMapTool(self.myMapTool)
            self.iface.mapCanvas().xyCoordinates.connect(self.mouseMove)
        else:
            self.disconnect()

    def mouseClick(self, currentPos, clickedButton):
        if clickedButton == Qt.LeftButton:  # and myRubberBand.numberOfVertices() == 0:
            self.myRubberBand.addPoint(QgsPointXY(currentPos))
            self.coordinates.append(QgsPointXY(currentPos))
            self.isEditing = 1

        elif clickedButton == Qt.RightButton and self.myRubberBand.numberOfVertices() > 2:
            self.isEditing = 0
            
            geomRubber = self.myRubberBand.asGeometry()

            layers = QgsProject.instance().mapLayers()
            for layer_id, layer in layers.items():
                new_geom = []
                layer.startEditing()
                features = layer.getFeatures()
                for feat in features:
                    geom = feat.geometry()
                    diff = geom.difference(geomRubber)
                    new_geom.append(diff)
                    feat.setGeometry(diff)
                    layer.changeGeometry(feat.id(), diff)
                # layer.updateExtents()
                    
            print(layers)
            # create feature and set geometry.

            # poly = QgsFeature()
            # geomP = self.myRubberBand.asGeometry()
            # poly.setGeometry(geomP)
            # g = geomP.asWkt()  # Get WKT coordenates.

            # canvas = self.iface.mapCanvas()

            # c = canvas.mapSettings().destinationCrs().authid()  # Get EPSG.
            # rep = c.replace("EPSG:", "")

            # vlyr = QgsVectorLayer("?query=SELECT geom_from_wkt('%s') as geometry&geometry=geometry:3:%s" % (
            #     g, rep), "Polygon_Reference", "virtual")

            # QgsProject.instance().addMapLayer(vlyr)

            # self.myRubberBand.reset(QgsWkbTypes.PolygonGeometry)

            # string = U"st_intersects(geom,st_geomfromewkt('SRID="+rep+";"+g+"'))"

            # layers = self.iface.mapCanvas().layers()

            # for layer in layers:
            #     try:
            #         layer.setSubsetString(string)
            #     except Exception:
            #         pass

            self.myRubberBand.reset(QgsWkbTypes.PolygonGeometry)
            self.disconnect()
            self.unChecked()

    def mouseMove(self, currentPos):
        if self.isEditing == 1:
            self.myRubberBand.movePoint(QgsPointXY(currentPos))
