#!/usr/bin/env gnuplot

# graph of various temperature sensors

# ******************************************************* General settings *****
set terminal png font "Helvetica" 11 size 640,480
set datafile separator ';'
set datafile missing "NaN"   # Ignore missing values
set grid
tz_offset = utc_offset / 3600 # GNUplot only works with UTC. Need to compensate
                              # for timezone ourselves.
set timestamp 'created: %Y-%m-%d %H:%M' bottom

# ************************************************************* Statistics *****
# stats to be calculated here
fname = "/tmp/sql25.csv"
stats fname using 2 name "T2" nooutput

T2_min = T2_min + utc_offset - 946684800
T2_max = T2_max + utc_offset - 946684800

# ****************************************************************** Title *****
set title "Temperature trends"
#"-".utc_offset."-"

# ***************************************************************** X-axis *****
set xlabel "Date/Time"       # X-axis label
set xdata time               # Define that data on X-axis should be interpreted as time
set timefmt "%s"             # Time in log-file is given in Unix format
set format x "%R"            # Display time in 24 hour notation on the X axis
set xtics rotate by 40 right
set xrange [ T2_min : T2_max ]

# ***************************************************************** Y-axis *****
set ylabel "Temperature [degC]"
#set yrange [10:20]
set autoscale y

# **************************************************************** Y2-axis *****
#set y2label "Raw values [mV]"
#set autoscale y2
#set y2tics border

# ***************************************************************** Legend *****
# generate a legend which is placed underneath the plot
#set key outside bottom center box title "-=legend=-"
set key default
set key box
set key samplen .2
set key inside vertical
set key left top

# ***************************************************************** Output *****
set object 1 rect from screen 0,0 to screen 1,1 behind
set object 1 rect fc rgb "#eeeeee" fillstyle solid 1.0 noborder
set object 2 rect from graph 0,0 to graph 1,1 behind
set object 2 rect fc rgb "#ffffff" fillstyle solid 1.0 noborder
set output "/tmp/bonediagd/Tdiag.png"

# ***** PLOT *****
plot "/tmp/sql21.csv"  using ($2+utc_offset):3 title "Room    [degC]"     with points pt 6 ps 0.2\
    ,"/tmp/sql22.csv"  using ($2+utc_offset):4 title "DHT22   [degC]"     with points pt 5 ps 0.2\
    ,"/tmp/sql23.csv"  using ($2+utc_offset):4 title "BMP183  [degC]"     with points pt 5 ps 0.2\
    ,"/tmp/sql24.csv"  using ($2+utc_offset):3 title "DS18B20 [degC]"     with points pt 5 ps 0.2\
    ,"/tmp/sql25.csv"  using ($2+utc_offset):3 title "TMP36   [degC]"     with dots\
