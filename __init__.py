# -*- coding: utf-8 -*-

def classFactory(iface):

    from .deleteFeatures import DeleteFeatures
    return DeleteFeatures(iface)