#!/usr/bin/env gnuplot

# graph of DHT22 data

# ******************************************************* General settings *****
set terminal png font "Helvetica" 11 size 640,480
set datafile separator ';'
set datafile missing "NaN"   # Ignore missing values
set grid
tz_offset = utc_offset / 3600 # GNUplot only works with UTC. Need to compensate
                              # for timezone ourselves.
set timestamp '%Y-%m-%d %H:%M' bottom

# ************************************************************* Statistics *****
# stats to be calculated here
fname = "/tmp/sql22.csv"
stats fname using 2 name "T2" nooutput

T2_min = T2_min + utc_offset - 946684800
T2_max = T2_max + utc_offset - 946684800

# ****************************************************************** Title *****
set title "Humidity (DHT22)"
#"-".utc_offset."-"

# ***************************************************************** X-axis *****
set xlabel "Date/Time"       # X-axis label
set xdata time               # Define that data on X-axis should be interpreted as time
set timefmt "%s"             # Time in log-file is given in Unix format
set format x "%R"            # Display time in 24 hour notation on the X axis
set xtics rotate by 40 right
set xrange [ T2_min : T2_max ]

# ***************************************************************** Y-axis *****
set ylabel "Humidity [%]"
#set yrange [10:20]
set autoscale y

# **************************************************************** Y2-axis *****
set y2label "Temperature [degC]"
set autoscale y2
set y2tics border

# ***************************************************************** Legend *****
# generate a legend which is placed underneath the plot
#set key outside bottom center box title "-=legend=-"
set key default
set key box
set key samplen .2
set key inside vertical
set key left top

# ***************************************************************** Output *****
set arrow from graph 0,graph 0 to graph 0,graph 1 nohead lc rgb "red" front
set arrow from graph 1,graph 0 to graph 1,graph 1 nohead lc rgb "green" front
set object 1 rect from screen 0,0 to screen 1,1 behind
set object 1 rect fc rgb "#eeeeee" fillstyle solid 1.0 noborder
set object 2 rect from graph 0,0 to graph 1,1 behind
set object 2 rect fc rgb "#ffffff" fillstyle solid 1.0 noborder
set output "/tmp/bonediagd/RHT.png"

# ***** PLOT *****
plot "/tmp/sql22.csv"  using ($2+utc_offset):3 title " Humidity [%]"      with points pt 5 ps 0.2\
    ,"/tmp/sql22.csv"  using ($2+utc_offset):4 title " Temperature [degC]" axes x1y2  with dots\
