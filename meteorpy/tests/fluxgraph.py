from meteorpy import flux
import matplotlib as mpl
import matplotlib.pyplot as plt

fg = flux.FluxGraph("PER", "2011-07-17", "2011-08-10", min_meteors=40, min_eca=40, min_interval=0, max_interval=9e99)
#fg._coveragePlot()
fg.show()

#plt.show()

#raw_input("Press Enter to continue...")
