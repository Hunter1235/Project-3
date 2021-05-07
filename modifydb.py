# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 21:09:21 2021
To test or demo the software it is not realistic to wait for CVS to change the
availity for their locations, so  we wrote this script to modify the database.

One city is deleted from the database so that the app can discover a city that 
isn't in the database.  Two have their status set to "Fully Booked" so the 
app will recognized them as locations with new availablity.  Atlanitc City is
much further away so that their will be a city outside to the users search
raduis (assuming they live near Kean University ;) )
@author: Hunter Stiles
"""

import sqlite3

con = sqlite3.connect('CVS_COVID.db')
cur = con.cursor()


cur.execute('DELETE FROM CVSLocations WHERE City = "hillside, NJ"')
cur.execute('UPDATE CVSLocations SET Status = "Fully Booked" where City = "union, NJ"')
cur.execute('UPDATE CVSLocations SET Status = "Fully Booked" where City = "atlantic city, NJ"')


con.commit()

    
cur.close()
con.close()