#CLUSTERING MODEL

from sklearn.cluster import SpectralClustering
from sklearn.mixture import GaussianMixture
from sklearn.clusters import KMeans
import pandas as pd

#Could look for clusters of negative and positive words by year or month 
#Can help to identify natural groups in the data

def create_clustering_model(X):
    
    #consider the number of clusters 
    n_clusters = add_number
    
    #fit it to the gmm model
    gmm_model = GaussianMixture(n_components=n_clusters)
    gmm_model.fit(X)
    
    #create cluster labels
    cluster_labels = gmm_model.predict(X)
    X = pd.DataFrame(X)
    X['cluster'] = cluster_labels
    
    #plot each cluster within a for loop
    for k in range(0,n_clusters):
    data = X[X["cluster"]==k]
    plt.scatter(data["Age"],data["Spending Score (1-100)"],c=color[k])
    
    #plot format
    plt.title("Clusters Identified by Guassian Mixture Model")    
    plt.ylabel("Word count") 
    plt.xlabel("Year")

