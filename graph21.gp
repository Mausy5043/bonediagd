#!/usr/bin/gnuplot

# graph of various temperature sensors

# ******************************************************* General settings *****
set datafile separator ';'
set datafile missing "NaN"   # Ignore missing values
set grid
tz_offset = utc_offset / 3600 # GNUplot only works with UTC. Need to compensate
                              # for timezone ourselves.

# ************************************************************* Statistics *****
# stats to be calculated here
fname = "/tmp/sql21.csv"
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
set xtics rotate by 45 right
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
set terminal png large
set output "/tmp/bonediagd/plot.png"

# ***** PLOT *****
plot "/tmp/sql21.csv"  using ($2+utc_offset):4 title " TMP36  [degC]"      with points pt 5 ps 0.2\
    ,"/tmp/sql22.csv"  using ($2+utc_offset):4 title " DHT22  [degC]"      with points pt 5 ps 0.2\
    ,"/tmp/sql23.csv"  using ($2+utc_offset):4 title " BMP183 [degC]"      with points pt 5 ps 0.2\
