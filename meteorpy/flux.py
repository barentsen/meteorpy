# -*- coding: utf-8 -*-
'''
Functions behind MetRec FluxViewer
'''
import sys
import numpy as np
import matplotlib as mpl
# Force matplotlib to not use any Xwindows backend.
if __name__ == '__main__':
    sys.path.append("/export/metrecflux/py/")
    mpl.use('Agg') 
import matplotlib.pyplot as plt

import datetime
import os
import pg

import vmo
import common

class FluxData(object):
    '''
    classdocs
    '''

    # Default binning parameters
    _min_meteors = 20
    _min_eca = 0
    _min_interval = 0.2 # Hours
    _max_interval = 24 # Hours
    _stations = ""
    _bin_mode = "adaptive"

    def __init__(self, shower, begin, end, **keywords):
        '''
        Constructor
        @shower: three-letter code
        @begin: Python datetime object
        @end: Python datetime object
        '''
        self._shower = shower
        self._begin = begin
        self._end = end
        # Set other parameters which have been supplied
        for kw in keywords.keys():
            self.__setattr__("_"+kw, keywords[kw])
            
        
    def _load(self):
        if self._stations != "":
            stationcond = " AND UPPER(station) = UPPER('%s') "  % pg.escape_string(self._stations)
        else:
            stationcond = ""
        
        """ SQL Query: fetch the raw counts """
        """
        if self._min_interval > 2:
            time = "time"
        else:
            time = "date_trunc('hour',time)"
        """    
        sql = """SELECT 
                    time, 
                    SUM(teff) AS teff, 
                    SUM(eca) AS eca, 
                    SUM(met) AS met,
                    COUNT(*) AS stations
                 FROM metrecflux
                 WHERE 
                     time >= '%s'::timestamp AND time <= '%s'::timestamp
                     AND shower = '%s' 
                     AND eca IS NOT NULL
                     AND eca >0.50
		     %s
                 GROUP BY time 
                 ORDER BY time""" % (pg.escape_string(str(self._begin)), pg.escape_string(str(self._end)), \
                                     pg.escape_string(self._shower), stationcond)
        result = vmo.sql(sql)
        if result != None:
            self._data = result
        else:
            self._data = []
        
    
    def _bin(self):
    	# Make sure data has been loaded
        if not hasattr(self, '_data'):
            self._load()
        # If data has been loaded but none is available, the result is the empty set!
        if len(self._data) == 0:
            self._bins = []
            return None
        
        # We should support different binning algorithms
        if self._bin_mode == "adaptive":
        	self._bin_adaptive()
        elif self._bin_mode == "fixed":
        	self._bin_fixed()
        else:
        	self._bin_adaptive()
    
    
    def _bin_adaptive(self):
        bins_time, bins_teff, bins_eca, bins_met = [], [], [], []
        
        current_bin_deltaseconds = []
        current_bin_start, current_bin_teff, current_bin_eca, current_bin_met = 0, 0, 0, 0
        for row in self._data:
            rowtime = datetime.datetime.strptime(row['time'], "%Y-%m-%d %H:%M:%S") 
            if current_bin_start == 0:
                current_bin_start = rowtime
            
            deltaseconds = self.diff_seconds(rowtime - current_bin_start)
            deltahours = deltaseconds/3600.0
            
            if (current_bin_met >= self._min_meteors \
                    and current_bin_eca >= (self._min_eca*1000.0) \
                    and deltahours >= self._min_interval) \
                or (deltahours >= self._max_interval):
                bins_time.append( current_bin_start+datetime.timedelta(seconds=np.mean(current_bin_deltaseconds)) )
                bins_teff.append( current_bin_teff )
                bins_eca.append( current_bin_eca )
                bins_met.append( current_bin_met )
                current_bin_deltaseconds = []
                current_bin_start, current_bin_teff, current_bin_eca, current_bin_met = rowtime, 0, 0, 0
        
            current_bin_deltaseconds.append( deltaseconds )
            current_bin_teff += row['teff']
            current_bin_eca += row['eca']
            current_bin_met += row['met']

        if current_bin_met > 5:
            bins_time.append( current_bin_start+datetime.timedelta(seconds=np.mean(current_bin_deltaseconds)) )
            bins_teff.append( current_bin_teff )
            bins_eca.append( current_bin_eca )
            bins_met.append( current_bin_met )
                
        time = np.array(bins_time)
        eca = np.array(bins_eca)
        teff = np.array(bins_teff)
        count = np.array(bins_met)
        # Units: meteoroids / 1000 km^2 h
        flux = 1000.0*((count+0.5)/eca) 
        e_flux = 1000.0*np.sqrt(count+0.5)/eca
        self._bins = {'shower':self._shower, \
                'time':time, 'teff':teff, \
                'flux':flux, 'e_flux':e_flux, \
                'met':count, 'eca':eca}


    def _bin_fixed(self):
    	# Lists to hold the bins
        bins_time, bins_teff, bins_eca, bins_met = [], [], [], []
        
        # Bin length
        bin_length = datetime.timedelta(self._min_interval/24.)
        
        # Temporary variables
        current_bin_end = self._begin + bin_length
        current_bin_teff, current_bin_eca, current_bin_met = 0, 0, 0
        
        # Loop over data
        for row in self._data:
        	# Convert SQL datetime string into Python datetime object
            rowtime = datetime.datetime.strptime(row['time'], "%Y-%m-%d %H:%M:%S") 
            
            # Create new bin if boundary passed
            if (rowtime >= current_bin_end):
                bins_time.append( current_bin_end - bin_length/2 )
                bins_teff.append( current_bin_teff )
                bins_eca.append( current_bin_eca )
                bins_met.append( current_bin_met )
                
                current_bin_end += bin_length
                current_bin_teff, current_bin_eca, current_bin_met = 0, 0, 0
            
            # Add data to current bin
            current_bin_teff += row['teff']
            current_bin_eca += row['eca']
            current_bin_met += row['met']
        
        # Final bin
        bins_time.append( current_bin_end - bin_length/2 )
        bins_teff.append( current_bin_teff )
        bins_eca.append( current_bin_eca )
        bins_met.append( current_bin_met )
                
        time = np.array(bins_time)
        eca = np.array(bins_eca)
        teff = np.array(bins_teff)
        count = np.array(bins_met)
        # Units: meteoroids / 1000 km^2 h
        flux = 1000.0*((count+0.5)/eca) 
        e_flux = 1000.0*np.sqrt(count+0.5)/eca
        self._bins = {'shower':self._shower, \
                'time':time, 'teff':teff, \
                'flux':flux, 'e_flux':e_flux, \
                'met':count, 'eca':eca}
    
	
    def getData(self):
        if not hasattr(self, '_data'):
            self._load()
        return self._data
    
    def getBins(self):
        if not hasattr(self, '_bins'):
            self._bin()
        return self._bins
    
    
    @staticmethod
    def diff_seconds(timedelta):
        """ Convert a datetime.timedelta object to a value in seconds """
        return (timedelta.days*3600.0*24.0 + timedelta.seconds + timedelta.microseconds/100000.0)
    
 
 
 
 
 
class FluxGraph(object):
    '''
    classdocs
    '''
    _debug = False
    _ymax = None

    def __init__(self, shower, begin, end, **keywords):
    	self._shower = shower
        # Convert ISO timestamps to Python DateTime objects
        self._begin = common.iso2datetime(begin)
        self._end = common.iso2datetime(end)

        # Set other parameters which have been supplied
        for kw in keywords.keys():
            self.__setattr__("_"+kw, keywords[kw])
        
        # Total number of seconds represented along X axis
        self._timespan = (self._end-self._begin).total_seconds()
        if self._timespan > (40*86400):
            raise Exception("Requested time interval too long.")
            
        
        self._fluxdata = FluxData(shower, self._begin, self._end, **keywords)

        
    
    def _createPlot(self):
        bins = self._fluxdata.getBins()
        
        self._fig = plt.figure(figsize=(11,6), dpi=80) # 11*80 = 880 pixels wide !
        ax = plt.subplot(111)
        self._fig.subplots_adjust(0.1,0.17,0.92,0.87)
                       
        ax_zhr = plt.twinx(ax=ax)
        ax_zhr.set_ylabel("ZHR", fontsize=16)
        ax_zhr.yaxis.set_major_formatter(plt.FuncFormatter(self.zhr_formatter))
        
        ax2 = plt.twiny(ax=ax)
        ax2.set_xlabel("Solar longitude (J2000.0)", fontsize=16)
        ax2.xaxis.set_major_formatter(plt.FuncFormatter(self.sollon_formatter))
          
        ax.grid(which="both")
        
        if len(bins) > 0:
            ax.errorbar(bins['time'], bins['flux'], yerr=bins['e_flux'], fmt="s", ms=4, lw=1.0, c='red' )    #fmt="+", ms=8    
        
        ax.set_xlim([self._begin, self._end])
        ax2.set_xlim([self._begin, self._end])
        ax_zhr.set_xlim([self._begin, self._end])
        
        # Determine the limit of the Y axis
        if self._ymax:
        	my_ymax = self._ymax
        else:
        	my_ymax = 1.1*max(bins['flux']+bins['e_flux'])
        
        if len(bins) > 0:
            ax.set_ylim([0, my_ymax])
            ax2.set_ylim([0, my_ymax])
            ax_zhr.set_ylim([0, my_ymax])        
        
        
        if self._timespan > 90*24*3600: # 90 days
            """ More than 5 days: only show dates """
            majorLocator = mpl.dates.AutoDateLocator(maxticks=10)
            sollonLocator = majorLocator
            majorFormatter = mpl.dates.DateFormatter('%d %b')
            xlabel = "Date (UT, %s)" % self._begin.year   
                    
        elif self._timespan > 5*24*3600: # 5 days
            """ More than 5 days: only show dates """
            majorLocator = mpl.dates.AutoDateLocator(maxticks=10)
            sollonLocator = majorLocator
            majorFormatter = mpl.dates.DateFormatter('%d %b')
            xlabel = "Date (UT, %s)" % self._begin.year   
        
        elif self._timespan > 1*24*3600:
            """ Between 1 and 5 days: show hours """
            majorLocator = mpl.dates.HourLocator(byhour=[0])
            majorFormatter = mpl.dates.DateFormatter('%d %b')
            
            if self._timespan > 3*24*3600:
                t = 12
            elif self._timespan > 1.5*24*3600:
                t = 6
            else:
                t = 3
            byhour = np.arange(t, 24, t)
            
            minorLocator = mpl.dates.HourLocator(byhour=byhour)
            ax.xaxis.set_minor_locator(minorLocator)
            sollonLocator = mpl.dates.HourLocator(byhour=np.append(0, byhour))
            fmt2 = mpl.dates.DateFormatter('%H:%M')        
            ax.xaxis.set_minor_formatter(plt.FuncFormatter(fmt2))
            xlabel = "Date (UT, %s)" % self._begin.year   
            
        else:
            if self._timespan > 18*3600:
                majorLocator = mpl.dates.HourLocator( np.arange(0, 24, 3) ) 
                minorLocator = mpl.dates.HourLocator( np.arange(0, 24, 1) ) 
            elif self._timespan > 12*3600:
                majorLocator = mpl.dates.HourLocator( np.arange(0, 24, 2) ) 
                minorLocator = mpl.dates.HourLocator( np.arange(1, 24, 2) ) 
            elif self._timespan > 6*3600:
                majorLocator = mpl.dates.HourLocator( np.arange(0, 24, 1) ) 
                minorLocator = mpl.dates.MinuteLocator(  np.arange(0,60,30)  )
            elif self._timespan > 3*3600:
                majorLocator = mpl.dates.MinuteLocator(  np.arange(0,60,30)  )
                minorLocator = mpl.dates.MinuteLocator(  np.arange(0,60,15)  )
            elif self._timespan > 1*3600:
                majorLocator = mpl.dates.MinuteLocator( np.arange(0,60,15) ) 
                minorLocator = mpl.dates.MinuteLocator(  np.arange(0,60,5) )
            else:
                majorLocator = mpl.dates.MinuteLocator( np.arange(0,60,10) ) 
                minorLocator = mpl.dates.MinuteLocator(  np.arange(0,60,2) )
                
            
            majorFormatter = mpl.dates.DateFormatter('%H:%M')  
            ax.xaxis.set_minor_locator(minorLocator)
            sollonLocator = majorLocator
            xlabel = "Time (UT, %s)" % self._begin.strftime('%d %b %Y')
        
        ax.xaxis.set_major_formatter(plt.FuncFormatter(majorFormatter))    
        ax2.xaxis.set_major_locator(sollonLocator)
        ax.xaxis.set_major_locator(majorLocator)
        
        
                
        ax.set_ylabel("Meteoroids / 1000$\cdot$km$^{2}\cdot$h", fontsize=18)
        ax.set_xlabel(xlabel, fontsize=18)
        
        labels = ax.get_xmajorticklabels()
        plt.setp(labels, rotation=45, fontsize=14) 
        labels = ax.get_xminorticklabels()
        plt.setp(labels, rotation=45, fontsize=12)
        
        #plt.close()
    
    def _coveragePlot(self):
        data = self._fluxdata.getData()
        
        self._figCoverage = plt.figure(figsize=(11,6), dpi=80) # 11*80 = 880 pixels wide !
        self._figCoverage.subplots_adjust(0.1,0.17,0.92,0.87, hspace=0)
        
        ax1 = plt.subplot(211)
        ax2 = plt.subplot(212)
        
        t = [datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in data['time']]
        ax1.bar(t, data['stations'], width=1.0/(24.0*60.0), edgecolor='none', facecolor='#ff4444')
        
        ax2.bar(t, data['met'], width=1.0/(24.0*60.0), edgecolor='none', facecolor='#ff4444')
        
        ax1.set_ylabel("Stations")
        ax2.set_ylabel("Meteors / minute")
        #ax.plot( t, data['met'] )
        #ax.plot( t, data['stations'], fillstyle="full" )
        
            
    def show(self):
        if not hasattr(self, '_fig'):
            self._createPlot()
        self._fig.show()        
        
    def savePlot(self, filename, dpi=100):
        if not hasattr(self, '_fig'):
            self._createPlot()
        self._fig.savefig(filename, dpi=dpi)
    
    
    def getFluxTable(self, format="html"):
        bins = self._fluxdata.getBins()
        if len(bins) == 0:
            html = "<div>No bins found</div>"
        else:
            """ Take a list of flux bins and produce a nice HTML table """
            html = "<table>\n"
            html += "\t<thead><th>Time<br/>[UT]</th><th>Solarlon<br/>[deg]</th><th>Teff<br/>[h]</th><th>ECA<br/>[10<sup>3</sup>&#183;km<sup>2</sup>&#183;h]</th>"
            html += "<th>n%s</th><th>Flux<br/>[10<sup>-3</sup>&#183;km<sup>-2</sup>&#183;h<sup>-1</sup>]</th><th>ZHR<sup>*</sup></th></thead>\n" % bins['shower']
            for i in range(len(bins['time'])):
                html += "\t<tr>"
                html += "<td>%s</td><td>%.3f</td><td>%.1f</td><td>%.1f</td><td>%d</td><td>%.1f &plusmn; %.1f</td><td>%.0f</td>" \
                    % ( str(bins['time'][i])[0:16], common.sollon(bins['time'][i]), bins['teff'][i]/60.0, bins['eca'][i]/1000.0, bins['met'][i], bins['flux'][i], bins['e_flux'][i], self.flux2zhr(bins['flux'][i], self._fluxdata._popindex) )
                html += "</tr>\n"
            html += "</table>"
            html += "<p style='text-align:center;'>(*) ZHR estimate derived following (<a href='http://adsabs.harvard.edu/abs/1990JIMO...18..119K'>Koschack &amp; Rendtel 1990b, Eqn. 41</a>)</p>"
        
        
        return html
    
    
    def getObserverTable(self, format="html"):
        if not hasattr(self, '_stationdata'):
            if self._fluxdata._stations != "":
                stationcond = " AND upper(station) = upper('%s') "  % pg.escape_string(self._fluxdata._stations)
            else:
                stationcond = ""
            
            sql = """SELECT a.station, a.observer, a.country, a.teff, a.eca, a.met, b.spo
                        FROM (
                        SELECT 
                            UPPER(station) AS station, 
                            MAX(meta.observer_firstname || ' ' || meta.observer_lastname) AS observer,
                            MAX(meta.site_country) AS country,
                            SUM(teff) AS teff, 
                            SUM(eca) AS eca, 
                            SUM(met) AS met 
                         FROM metrecflux AS x
                         LEFT JOIN metrecflux_meta AS meta ON x.filename = meta.filename
                         WHERE time BETWEEN '%s' AND '%s' 
                         AND shower = '%s'
        	         AND eca IS NOT NULL
	                 AND eca > 0.00
                         %s
                         GROUP BY UPPER(station)
                         ORDER BY UPPER(station) ) AS a
                         
                        LEFT JOIN (
                            SELECT 
                                UPPER(station) AS station, SUM(met) AS spo
                            FROM 
                                metrecflux
                            WHERE 
                                time BETWEEN '%s' AND '%s' 
                                AND shower= 'SPO'
    		                AND eca IS NOT NULL
                		AND eca > 0.00
                            GROUP BY UPPER(station)
                        ) AS b ON a.station = b.station        
                         """ % (pg.escape_string(str(self._begin)), pg.escape_string(str(self._end)), \
                                pg.escape_string(self._shower), stationcond, \
                                pg.escape_string(str(self._begin)), pg.escape_string(str(self._end)))
            self._stationdata = vmo.sql(sql)
        
            if self._stationdata == None:
                return ""
    
        html = u"<table>\n"
        html += u"\t<thead><th style='text-align:left;'>Station<br/> </th><th style='text-align:left;'>Observer<br/> </th><th style='text-align:left;'>Country<br/> </th>"
        html += u"<th>Teff<br/>[h]</th><th>ECA<br/>[10<sup>3</sup>&#183;km<sup>2</sup>&#183;h]</th><th>n%s<br/> </th><th>nSPO<br/> </th></thead>\n" % self._shower
        
        for row in self._stationdata:
            html += u"\t<tr><td style='text-align:left;'>%s</td><td style='text-align:left;'>%s</td><td style='text-align:left;'>%s</td>" % (row['station'], row['observer'].decode("utf-8"), row['country'])
            html += u"<td>%.0f</td><td>%.0f</td><td>%d</td><td>%d</td></tr>\n" % (row['teff']/60.0, row['eca']/1000.0, row['met'], row['spo'])
            
        html += u"<table>\n"
        return html
    
    
    @staticmethod
    def flux2zhr(flux, pop_index=2.0):
        """ 
        Flux in 1000^-1 km^-2 h^-2 
        
        Eqn 41 from (Koschak 1990b)
        """    
        r = pop_index
        flux = flux / 1000.0
        zhr = (flux * 37200.0) / ( (13.1*r - 16.45) * (r - 1.3)**0.748 )
        return zhr
    
    
    def sollon_formatter(self, a, b):
        """
        a: ordinal datetime
        b: tick nr 
        Usage: ax.xaxis.set_major_formatter(pylab.FuncFormatter(sollon_formatter)) 
        """
        
        
        # 10 days
        if self._timespan > 10*24*3600:
            fmt = "%.1f"
        # 1 day
        elif self._timespan > 24*3600:
            fmt = "%.2f"
        else:
            fmt = "%.3f"
        
        d = datetime.datetime.fromordinal(int(a))+datetime.timedelta(a-int(a))
        return fmt % common.sollon(d)

    def date_formatter(self, a, b):
        """
        a: ordinal datetime
        b: tick nr 
        Usage: ax.xaxis.set_major_formatter(pylab.FuncFormatter(sollon_formatter)) 
        """
        d = datetime.datetime.fromordinal(int(a))+datetime.timedelta(a-int(a))
        
        if self._timespan > 56*3600:
            fmt = '%d %b'
        else:
            fmt = '%H:%M\n(%d %b)'
        
        return d.strftime(fmt)

    def zhr_formatter(self, a, b):
        zhr = FluxGraph.flux2zhr(a, self._fluxdata._popindex)
        if round(zhr) < 10:
            return "%.1f" % zhr
        else:
        	return "%.0f" % zhr
        
    


class FluxPage(object):
    """ HTML overview of the meteoroid flux """
    def __init__(self, shower, begin, end, **keywords):           
        self._fluxgraph = FluxGraph(shower, begin, end, **keywords)    
    
    
    def printHTML(self, output, plotdir):        
        # Make sure the directory to save plots exists
        try:
            os.makedirs(plotdir)
        except OSError:
            pass # Dir already exists
            
            
        prefix = "%s_%06d" % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"), np.random.uniform(0,999999))
        self._fluxgraph.savePlot("%s/%s.png" % (plotdir, prefix), dpi=80)
        
        html = ""
        html += "<div id='fluxplot' style='text-align:center;'>\n"
        html += "<img src='/flx/tmp/%s.png'/>\n" % prefix
        if output == "full":
            html += "<br/>(High-resolution: <a href='/flx/tmp/%s.pdf'>PDF</a> | <a href='/flx/tmp/%s_dpi300.png'>PNG</a>)\n" % (prefix, prefix)
        html += "</div>\n"
        print html.encode("utf8")
        sys.stdout.flush()
    
        if output == "full":
            html = ""
            html += "<div id='fluxtable'>\n"
            html += self._fluxgraph.getFluxTable(format="html")
            html += "</div>\n"
            print html.encode("utf8")
            sys.stdout.flush()

            self._fluxgraph.savePlot("%s/%s_dpi300.png" % (plotdir, prefix), dpi=300)
            self._fluxgraph.savePlot("%s/%s.pdf" % (plotdir, prefix), dpi=100)
            
            html = ""
            html += "<div id='showertable'>\n"
            html += self._fluxgraph.getObserverTable(format="html")
            html += "</div>\n"
            print html.encode("utf8")
            sys.stdout.flush()
            

        


if __name__ == '__main__':
    """
    Example: python flux.py -d /tmp LYR 2011-04-21T18:00:00 2011-04-24T06:00:00
    """
    time_start = datetime.datetime.now()
    
    from optparse import OptionParser
    usage = "usage: %prog [options] shower begin end"
    parser = OptionParser(usage)
    parser.add_option("-b", "--bin-mode", dest="bin_mode", default="adaptive", type="string", \
                      metavar="BINMODE", help="binning algorithm to use, default = adaptive")
    parser.add_option("-m", "--min-meteors", dest="min_meteors", default="20", type="int", \
                      metavar="N", help="minimum number of meteors per bin, default = 20")
    parser.add_option("-e", "--min-eca", dest="min_eca", default="0", type="float", \
                      metavar="F", help="minimum ECA per bin, default = 0")
    parser.add_option("-i", "--min-interval", dest="min_interval", default="1.0", type="float", \
                      metavar="HOURS", help="minimum bin length, default = 1 h")
    parser.add_option("-j", "--max-interval", dest="max_interval", default="24.0", type="float", \
                      metavar="HOURS", help="maximum bin length, default = 24 h")
    parser.add_option("-r", "--popindex", dest="popindex", default="2.0", type="float", \
                      metavar="POPINDEX", help="population index")
    parser.add_option("-y", "--ymax", dest="ymax", default=None, type="float", \
                      metavar="YMAX", help="maximum limit of the Y axis")
    parser.add_option("-s", "--stations", dest="stations", default="", type="string", \
                      metavar="STATIONS", help="stations separated by commas")
    parser.add_option("-d", "--plot-dir", dest="plot_dir", default="/export/metrecflux/public_html/tmp/", type="string", \
                      metavar="DIR", help="where to store the graphs?")      
    parser.add_option("-o", "--output", dest="output", default="full", type="string", \
                      metavar="MODE", help="what to output? (e.g. graph, full)")      
    (opts, args) = parser.parse_args()
    
    if len(args) != 3:
        print "Error: need at least 3 arguments"
    
    fg = FluxPage(args[0], args[1], args[2], \
    			   bin_mode=opts.bin_mode, ymax=opts.ymax, \
                   min_meteors=opts.min_meteors, min_eca=opts.min_eca, \
                   min_interval=opts.min_interval, max_interval=opts.max_interval, \
                   popindex=opts.popindex, stations=opts.stations)
    fg.printHTML(output=opts.output, plotdir=opts.plot_dir)
    
    time_finish = datetime.datetime.now()
    print "<div>Computation time: %.1f s</div>" % ( (time_finish-time_start).total_seconds() )

