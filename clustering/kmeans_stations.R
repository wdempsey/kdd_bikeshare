library(ggplot2)
library(ggmap)
library(mapproj)

# read in stations
stations <- read.csv("~/bikeshare_data/stations.csv")[1:4]
colnames(stations) <- c('id','name','latitude','longitude')

# quick viz of the stations
ggplot(stations, aes(x=latitude, y=longitude)) + geom_point(shape=1) 

# calculate distance in the l1-norm
l1_dist = dist(stations[,c('latitude','longitude')], method = 'manhattan')
# dendrogram
dendro <- hclust(l1_dist, method="single")
plot(dendro,  main = "Cluster Dendrogram of Station Data Using Single Link (Manhattan Metric)")
# from examining the plot, 8 or 9 clusters looks reasonable 

# run k-means
set.seed(123)
n_cluster = 8
cluster = kmeans(l1_dist, centers = n_cluster, iter.max = 100, nstart = 9)
plot(stations[,c('latitude','longitude')], col = cluster$cluster, main = paste('K-means Clustering using l1 distance, clusters = ',n_cluster,sep = ''), pch = 15)
points(cluster$centers, col = 1:2, pch = 8, cex = 2)

stations$cluster = cluster$cluster

write.table(stations, file = "~/bikeshare_data/stations_with_cluster.csv")

# build a map with the stations color-coded by cluster
map <- get_map(location = 'Washington, DC', source = 'osm', maptype = "roadmap", zoom = 12)

stations$Cluster = as.character(cluster$cluster)
mapPoints <- ggmap(map) + geom_point(aes(x = longitude, y = latitude, colour = Cluster), data = stations, size = 2) + scale_colour_hue(l=30) +
  labs(title = '',
                                                 x = 'Latitude',
                                                 y = 'Longitude') #+ coord_cartesian(xlim = c(-77.15,-76.9), ylim = c(38.84,38.96)) 
mapPoints

mapPoints <- ggmap(map) + geom_point(aes(x = longitude, y = latitude), data = stations) + scale_colour_hue(l=30) +
  labs(title = '',
       x = 'Latitude',
       y = 'Longitude') #+ coord_cartesian(xlim = c(-77.15,-76.9), ylim = c(38.84,38.96)) 
mapPoints
