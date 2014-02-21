library(Hmisc)
library(ggplot2)

# read in the arrival data
corr_10 <- read.csv("~/corr_10.csv", header=F)
corr_54 <- read.csv("~/corr_54.csv", header=F)
corr_106 <- read.csv("~/corr_106.csv", header=F)

# read in stations and calculate distance
#stations_with_cluster <- read.table("~/repos/kdd_bikeshare/clustering/stations_with_cluster.csv", header=T, quote="\"")
#s= stations_with_cluster
#stations = s[s$id == 10 | s$id == 54 | s$id == 106, c('id','latitude','longitude')]
#dist_btw_stations = dist(stations, method = 'manhattan')
#dists = as.matrix(round(dist_btw_stations, digits = 2))

# calculate pairwise correlation 
c_106_54 = cor(cbind(corr_106[,2],corr_54[,2]), method="pearson")
c_10_106 = cor(cbind(corr_106[,2],corr_10[,2]), method="pearson")
c_10_54 = cor(cbind(corr_106[,2],corr_54[,2]), method="pearson")

# make dataframe for plot 
# Note: first value in the vector is the distance in miles that I straight looked-up
# on GoogleMaps #winning
row1= c(4.7,round(c_10_54[1,2], digits = 2), 'between station 10 and 54')
row2 = c(4.6,round(c_10_106[1,2], digits = 2), 'between station 10 and 106')
row3 = c(.05,round(c_106_54[1,2], digits = 2), 'between station 54 and 106')
plot = as.data.frame(rbind(rbind(row1,row2),row3))
colnames(plot) = c('Distance','Correlation','Relationship')

ggplot(data =  plot, aes(x = Distance, y = Correlation, colour = Relationship))  + geom_point()








