#!/usr/bin/gnuplot

# graph of DHT22 data

# ******************************************************* General settings *****
set terminal png font "Helvetica" 11
set datafile separator ';'
set datafile missing "NaN"   # Ignore missing values
set grid
tz_offset = utc_offset / 3600 # GNUplot only works with UTC. Need to compensate
                              # for timezone ourselves.

# ************************************************************* Statistics *****
# stats to be calculated here
fname = "/tmp/sql23.csv"
stats fname using 2 name "T2" nooutput

T2_min = T2_min + utc_offset - 946684800
T2_max = T2_max + utc_offset - 946684800

# ****************************************************************** Title *****
set title "Air Pressure (BMP183) @ NAP+12.1m"
# groundlevel = +8.5m
# sensor at +3.5 above groundlevel
#"-".utc_offset."-"

# ***************************************************************** X-axis *****
set xlabel "Date/Time"       # X-axis label
set xdata time               # Define that data on X-axis should be interpreted as time
set timefmt "%s"             # Time in log-file is given in Unix format
set format x "%R"            # Display time in 24 hour notation on the X axis
set xtics rotate by 40 right
set xrange [ T2_min : T2_max ]

# ***************************************************************** Y-axis *****
set ylabel "Pressure [mbar]"
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
set output "/tmp/bonediagd/plot3.png"

# ***** PLOT *****
plot "/tmp/sql23.csv"  using ($2+utc_offset):3 title " Pressure [mbar]"      with points pt 5 ps 0.2\
    ,"/tmp/sql23.csv"  using ($2+utc_offset):4 title " Temperature [degC]" axes x1y2  with dots\
