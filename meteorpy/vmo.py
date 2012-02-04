'''
Connect to the PostgreSQL VMO database
'''
import numpy as np
import pg   # Provided by Debian package "python-pygresql"
import ConfigParser


class VMO(object):
    '''
    classdocs
    '''

    db = None

    def __init__(self):
        '''
        Constructor
        '''
        config = ConfigParser.ConfigParser()
        config.read("config/vmo.ini")
        self.db = pg.connect(host=config.get("DB", "host"), port=config.get("DB", "port"), \
                             dbname=config.get("DB", "name"), \
                             user=config.get("DB", "user"), passwd=config.get("DB", "pass"))
        
     
       
    def sql2recarray(self, sql):
        if self.db == None:
            self.connect()
        
        q = self.db.query(sql)
        results = q.getresult()
        if len(results) == 0:
            return None
        # What is the data type of each row?
        formats = []
        for col in results[0]:
            t = str(np.dtype(col.__class__))
            if t == "|S0":
                # Due to a stupid bug in numpy, we need to set a fixed length for a string
                t = "|S9999"
            formats.append( t )
        dt = np.dtype({'names':q.listfields(), 'formats':formats})
        r = np.array(results, dt)
        return r
 

""" Allow single-line queries """
default = None
def sql(sql):
    if default == None:
        vmo = VMO()
    return vmo.sql2recarray(sql)

