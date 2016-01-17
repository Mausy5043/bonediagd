#!/usr/bin/gnuplot

# graph of TMP36


# ******************************************************* General settings *****
set datafile separator ';'
set datafile missing "NaN"   # Ignore missing values
set grid
tz_offset = utc_offset / 3600 # GNUplot only works with UTC. Need to compensate
                              # for timezone ourselves.

# ************************************************************* Statistics *****
# stats to be calculated here
fname = "/tmp/sql22.csv"
stats fname using 2 name "T2" nooutput

T2_min = T2_min + utc_offset - 946684800
T2_max = T2_max + utc_offset - 946684800

# ****************************************************************** Title *****
set title "DHT22 measurements"
#"-".utc_offset."-"

# ***************************************************************** X-axis *****
set xlabel "Date/Time"       # X-axis label
set xdata time               # Define that data on X-axis should be interpreted as time
set timefmt "%s"             # Time in log-file is given in Unix format
set format x "%R"            # Display time in 24 hour notation on the X axis
set xtics rotate by 45 right
set xrange [ T2_min : T2_max ]

# ***************************************************************** Y-axis *****
set ylabel "Temperature [degC]" # Title for Y-axis
#set yrange [10:20]
set autoscale y

# **************************************************************** Y2-axis *****
set y2label "Humidity [%]" # Title for Y2-axis
set autoscale y2
set y2tics border         # place ticks on second Y2-axis

# ***************************************************************** Legend *****
# generate a legend which is placed underneath the plot
set key outside bottom center box title "-=legend=-"

# ***************************************************************** Output *****
set terminal png large
set output "/tmp/bonediagd/plot2.png"

# ***** PLOT *****
plot "/tmp/sql22.csv"  using ($2+utc_offset):4 title "Temperature [degC]"      with points pt 5 ps 0.2\
    ,"/tmp/sql22.csv"  using ($2+utc_offset):3 title "Humidity [%]" axes x1y2  with points pt 5 ps 0.2\
