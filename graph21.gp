#!/usr/bin/gnuplot

# graph of TMP36

# ************************************************************* Statistics *****
# stats to be calculated here

# ******************************************************* General settings *****
set datafile separator ';'
set datafile missing "NaN"   # Ignore missing values
set grid

# ****************************************************************** Title *****
set title "Test graph -".tz_gap."-"

# ***************************************************************** X-axis *****
set xlabel "Date/Time"       # X-axis label
set xdata time               # Define that data on X-axis should be interpreted as time
set timefmt "%s"             # Time in log-file is given in Unix format
set format x "%R"            # Display time in 24 hour notation on the X axis
set xtics rotate by 45 right

# ***************************************************************** Y-axis *****
set ylabel "Temperature [degC]" # Title for Y-axis
set yrange [15:20]
#set autoscale y

# **************************************************************** Y2-axis *****
set y2label "Raw values [mV]" # Title for Y2-axis
set autoscale y2
set y2tics border         # place ticks on second Y2-axis

# ***************************************************************** Legend *****
# generate a legend which is placed underneath the plot
set key outside bottom center box title "-=legend=-"

# ***************************************************************** Output *****
set terminal png large
set output "/tmp/bonediagd/plot.png"

# Data columns are:
# 2 is Unix Epoch time
# 3 is TMP36 mV
# 4 is calculated temperature

# ***** PLOT *****
plot "/tmp/sql21.csv"    using ($2+tz_gap):4 title "Temperature [degC]"      with lines \
                  ,""    using ($2+tz_gap):3 title "Raw signal [mV]"         with lines axes x1y2 \
     ,"/tmp/sql21b.csv"  using ($2+tz_gap):3 title "Room temperature [degC]" with lines \
