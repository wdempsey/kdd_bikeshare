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
plot(stations_mat, col = cluster$cluster, main = paste('K-means Clustering using l1 distance, clusters = ',n_cluster,sep = ''), pch = 15)
points(cluster$centers, col = 1:2, pch = 8, cex = 2)

stations$cluster = cluster$cluster

write.table(stations, file = "~/bikeshare_data/stations_with_cluster.csv")

# build a map with the stations color-coded by cluster
map <- get_map(location = 'Washington, DC', maptype = "roadmap", zoom = 11)

stations$cluster = as.character(cluster$cluster)
mapPoints <- ggmap(map) + geom_point(aes(x = longitude, y = latitude, colour = cluster), data = stations, alpha = .5, size = 3) + scale_colour_hue(l=30) +
  labs(title = 'Clustering of Bikeshare Stations in Washington, D.C.',
                                                 x = 'Latitude',
                                                 y = 'Longitude') 
mapPoints
