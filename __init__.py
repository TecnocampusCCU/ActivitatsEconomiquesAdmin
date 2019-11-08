# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ActivitatsEconomiquesAdmin
                                 A QGIS plugin
 ActivitatsEconomiquesAdmin
                             -------------------
        begin                : 2018-05-24
        copyright            : (C) 2018 by ccu
        email                : jlopez@tecnocampus.cat
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ActivitatsEconomiquesAdmin class from file ActivitatsEconomiquesAdmin.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .ActivitatsEconomiquesAdmin import ActivitatsEconomiquesAdmin
    return ActivitatsEconomiquesAdmin(iface)
