#!/usr/bin/gnuplot

set datafile separator ';'

# Title of the plot
set title "Test graph"

# We want a grid
set grid

# Ignore missing values
#set datafile missing "NaN"

# X-axis label
set xlabel "Date/Time"

# set X-axis range to current date only
#set xrange ["$YESTERDAY":"$TODAY"]

# Y-axis ranges from 0 deg C to 100 deg C, same scale as for humidity
set yrange [15:20]

# Y2-axis set from 800 to 1200 kPa, used for barometric pressure
set autoscale y2

# place ticks on second Y2-axis
set y2tics border

# Title for Y-axis
set ylabel "Temperature [degC]"

# Title for Y2-axis
set y2label "Raw values [mV]"

# Define that data on X-axis should be interpreted as time
set xdata time

# Time in log-file is given in Unix format
set timefmt "%s"

# Display notation for time
set format x "%D\n%R"    # Display time in 24 hour notation on the X axis

# generate a legend which is placed underneath the plot
set key outside bottom center box title "--legend--"

# output into png file
set terminal png large
set output "/tmp/bonediagd/plot.png"

# Data columns are:
# 2 is Unix Epoch time
# 3 is TMP36 mV
# 4 is calculated temperature

# read data from file and generate plot
plot "/tmp/sql.csv" using 2:4 title "Temperature [degC]" with lines \
                ,"" using 2:3 title "Raw signal [mV]" with lines axes x1y2 \
