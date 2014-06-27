tephi
=====

Tephigram plotting in Python.

The tephi module provides plotting of tephigrams from ASCII text files. 

A function is provided to load text files into a data structure that may be used for plotting tephigrams with tephi::

    >>> import os.path
    >>> import tephi
    >>> winds = os.path.join(tephi.RESOURCES_DIR, 'barbs.txt')
    >>> columns = ('pressure', 'dewpoint', 'wind_speed', 'wind_direction')
    >>> barbs = tephi.loadtxt(winds, column_titles=columns)
    >>> barbs
    tephidata(
        pressure=array([ 1006.,   924.,   900.,   850.,   800.,   755.,   710.,   700.,
             600.,   500.,   470.,   459.,   400.,   300.,   250.], dtype=float32)
        dewpoint=array([ 26.39999962,  20.29999924,  19.79999924,  14.5       ,
            12.89999962,   8.30000019,  -5.        ,  -5.0999999 ,
           -11.19999981,  -8.30000019, -12.10000038, -12.5       ,
           -32.90000153, -46.        , -53.        ], dtype=float32)
        wind_speed=array([  0.,   1.,   5.,   5.,   7.,  10.,  12.,  15.,  25.,  35.,  40.,
            43.,  45.,  50.,  55.], dtype=float32)
        wind_direction=array([   0.,   15.,   25.,   30.,   60.,   90.,  105.,  120.,  180.,
            240.,  270.,  285.,  300.,  330.,  359.], dtype=float32))
    
These data structures can then be used to plot a tephigram::

    >>> dews = zip(barbs.pressure, barbs.dewpoint)
    >>> barb_vals = zip(barbs.wind_speed, barbs.wind_direction, barbs.pressure)
    >>> tpg = tephi.Tephigram()
    >>> profile = tpg.plot(dews)
    >>> profile.barbs(barb_vals)
    >>> plt.show()
