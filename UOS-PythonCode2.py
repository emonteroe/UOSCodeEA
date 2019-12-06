#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 16:40:04 2019

@author: emanuel
"""
from sklearn.cluster import DBSCAN
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
from matplotlib import pyplot as plt
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
from pandas import DataFrame
from sklearn import metrics
import statistics
import csv
import math
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error
from pandas.plotting import autocorrelation_plot
from pykalman import KalmanFilter


def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

def read_file(filename, node_id, coord = "x"):
    with open(filename) as f:
        if coord == "x":
            lines = [float(i.split()[5]) for i in f.readlines() if
                     "node_({})".format(node_id) in i
                    and "setdest" in i]
        elif coord == "y":
            lines = [float(i.split()[6]) for i in f.readlines() if
                     "node_({})".format(node_id) in i
                    and "setdest" in i]
        else:
            raise ValueError("invalid coordinate")
        return lines
    
def arima():

    mse = []

    for i in range (100):
        observations_x = read_file("scratch/UOS_UE_Scenario_5.ns_movements", i, "y")
        print (len(observations_x))
        

        size = int(len(observations_x) * 0.26)
        train, test = observations_x[0:size], observations_x[size:len(observations_x)]
        history = [x for x in train]
        predictions_x = []

        for i, v in enumerate(test):
            model = ARIMA(history, order=(5,1,0))
            model_fit = model.fit(disp=0)
            output = model_fit.forecast()
            # print(model_fit.summary())
            yhat = output[0]
            predictions_x.append(yhat)
            obs = v
            history.append(obs)

        error = mean_squared_error(test, predictions_x)
        # print('Test MSE: %.3f' % error)
        mse.append(error)

    return mse

def kalman():
    error = []
    for i in range (100):
        observations_x = read_file("scratch/UOS_UE_Scenario_5.ns_movements", i, "x")
        observations_y = read_file("scratch/UOS_UE_Scenario_5.ns_movements", i, "y")

        kf = KalmanFilter(transition_matrices=np.array([[1, 1], [0, 1]]),
                          transition_covariance=0.01 * np.eye(2))
        states_pred_x = kf.em(observations_x).smooth(observations_x)[0]
        states_pred_y = kf.em(observations_y).smooth(observations_y)[0]

        mse = sum((states_pred_x[:, 0] - observations_x)**2) / len(observations_x)
 
    return (states_pred_x[:,0], states_pred_y[:,0])
        #error.append(mse)
    #return error

#Arima = arima()
#print(Arima)
#Kalman = kalman()
#print(Kalman)

def DBSCAN_Clusterization(X, EPS, MIN_SAMPLES):
    
    DBClusters = DBSCAN(eps=1000, min_samples=8, metric ='euclidean',algorithm = 'auto')#'kd_tree')
    DBClusters.fit(X)
    #DBClusters.labels_
    
    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(DBClusters.labels_)) - (1 if -1 in DBClusters.labels_ else 0)
    core_samples = np.zeros_like(DBClusters.labels_, dtype = bool)
    core_samples[DBClusters.core_sample_indices_] = True
    
    # PRINT CLUSTERS & # of CLUSTERS
    print("Clusters:"+str(DBClusters.labels_))
    
    print('Estimated number of clusters: %d' % n_clusters_)
    
    clusters = [X[DBClusters.labels_ == i] for i in range(n_clusters_)]
    outliers = X[DBClusters.labels_ == -1]
    
    # Plot Outliers
    plt.scatter(outliers[:,0], outliers[:,1], c="black", label="Outliers")
    
    
    # Plot Clusters
    cmap = get_cmap(len(clusters))
    x_clusters = [None] * len(clusters)
    y_clusters = [None] * len(clusters)
    #colors = [0]
    colors = "bgrcmykw"
    color_index = 0
    for i in range(len(clusters)):
        x_clusters[i] = []
        y_clusters[i] = []
       # print("Tamano Cluster "+ str(i) + ": " + str(len(clusters[i])))
        for j in range(len(clusters[i])):
            x_clusters[i].append(clusters[i][j][0])
            y_clusters[i].append(clusters[i][j][1])
            
    #        
        
        plt.scatter(x_clusters[i], y_clusters[i], label= "Cluster %d" %i,  s=8**2, c=colors[color_index]) #c=cmap(i)) 
        color_index += 1
        
    
    #plot the Clusters 
    #plt.title("Clusters Vs Serving UABS")
    plt.scatter(x2,y2,c="yellow", label= "UABSs", s=10**2) #plot UABS new position
    plt.xlabel('x (meters)', fontsize = 16)
    plt.ylabel('y (meters)', fontsize = 16)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
              fancybox=True, shadow=True, ncol=5)
    plt.savefig("Graph_Clustered_UOS_Scenario.pdf", format='pdf', dpi=1000)
    plt.show()      
    
    return clusters, x_clusters, y_clusters  
    
#-----------------------------------Main----------------------------------------------------------------   

# generate 2d classification dataset (this will represent the users and the eNodeBs)
#X, y = make_blobs(n_samples=10000, centers= 4, n_features=2, shuffle = False, cluster_std=1.2)
# scatter plot, dots colored by class value
#print(X.shape)


with open('enBs') as fenBs:
    data1 = np.array(list((float(x), float(y), float(z), int(cellid)) for x, y, z, cellid in csv.reader(fenBs, delimiter= ',')))
    
with open('LTEUEs') as fUEs:
    data2 = np.array(list((float(x), float(y), float(z)) for x, y, z in csv.reader(fUEs, delimiter= ',')))
    
with open('UABSs') as fUABS:
    data3 = np.array(list((float(x), float(y), float(z), int(cellid)) for x, y, z, cellid in csv.reader(fUABS, delimiter= ',')))

with open('UEsLowSinr') as fUEsLow:
    data4 = np.array(list((float(x), float(y), float(z), float (Sinr), int (Imsi),int(cellid)) for x, y, z, Sinr,Imsi, cellid in csv.reader(fUEsLow, delimiter= ',')))

with open('UABS_Energy_Status') as fUABS_Energy:
    data5 = np.array(list((int(time), int(UABSID), int(Remaining_Energy)) for time, UABSID, Remaining_Energy in csv.reader(fUABS_Energy, delimiter= ',')))

with open('UEs_UDP_Throughput_RUN_') as fUE_Throughput:
    data6 = np.array(list((int(time), int(UE_ID), float(x), float(y), float(z), float(UE_Throughput)) for time, UE_ID, x, y, z, UE_Throughput in csv.reader(fUE_Throughput, delimiter= ',')))


#print("enBs: "+ str(data1))
#print("UEs: "+ str(data2))
#print("UABSs: "+ str(data3))
#print("UEsLowSinr: "+ str(data4[0:2][0]))
x,y,z, cellid= data1.T
plt.scatter(x,y,c="blue", label= "enBs", s=15**2)

x1,y1,z1= data2.T
plt.scatter(x1,y1,c="gray", label= "UEs")

x2,y2,z2, cellid3= data3.T
plt.scatter(x2,y2,c="yellow", label= "UABSs", s=10**2)
UABSCoordinates = np.array(list(zip(x2,y2)))

x3,y3,z3, sinr, imsi, cellid4= data4.T
X = np.array(list(zip(x3,y3)))
#X = StandardScaler().fit_transform(X)
#print(X)

plt.scatter(x3,y3,c="red", label= "UEsLowSINR")

time, Uabs_Id, Remaining_Energy = data5.T

time_UE, UE_ID, x4, y4, z4, UE_Throughput = data6.T
## ----------------Here i have to just create a X Y pair with lowest throughput users.
X1 = np.array(list(zip(x4,y4)))

#circle2 = plt.Circle((0.5, 0.5), 0.2, color='blue', fill=False)
#fig, ax = plt.subplots()
#ax.add_artist(circle2)

#plt.title('LTE + UOS')
plt.xlabel('x (meters)', fontsize = 16)
plt.ylabel('y (meters)', fontsize = 16)
plt.legend( loc='upper right',bbox_to_anchor=(1.1, 1.05),
          fancybox=True, shadow=True, ncol=1)
#plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
#          fancybox=True, shadow=True, ncol=5)
plt.savefig("Graph_Initial_UOS_Scenario.pdf", format='pdf', dpi=1000)
plt.show()
#print(X.size)

#---------------Clustering with DBSCAN for Users with Low SINR---------------------
eps=1000
min_samples=8
clusters, x_clusters, y_clusters = DBSCAN_Clusterization(X, eps, min_samples)


#---------------Clustering with DBSCAN for Users with Low Throughput---------------------
eps=1000
min_samples=8
DBSCAN_Clusterization(X1, eps, min_samples)
 


#Sum of SINR and mean to later prioritize the clusters  
SUMSinr = [None] * len(clusters)

for i in range(len(clusters)):
    SUMSinrClusters = 0
    for j in range(len(clusters[i])):
        index_x3 = np.where(x3 == clusters[i][j][0])
#        print("Found x3: "+str(np.where(x3 == clusters[i][j][0]))) # para comparar con x3
#        print("Found y3: "+str(np.where(y3 == clusters[i][j][1]))) # para comparar con x3
        for k in range(len(index_x3)):
            if (y3[index_x3[k]] == clusters[i][j][1]):
#                print("SINR FOUND: " + str(sinr[index_x3[k]]))
                SUMSinrClusters += sinr[index_x3[k]]
#                print(sinr[index_x3[k]])
#                print(SUMSinrClusters)
#   SUMSinr[i] = sinr[index_x3[k]]
    SUMSinr[i] = SUMSinrClusters        

SINRAvg = [None] * len(clusters)

for i in range(len(SUMSinr)):
    SINRAvg[i] = SUMSinr[i]/len(clusters[i])

#Prioritize by greater SINR    
CopySINRAvg = SINRAvg.copy()
SINRAvgPrioritized = []
for i in range(len(SINRAvg)):
    #print("SINR Max:" + str(max(CopySINRAvg)))
    SINRAvgPrioritized.append(min(CopySINRAvg))  #evaluar si es MAX o MIN que quiero para obtener el cluster con mayor SINR
    CopySINRAvg.remove(min(CopySINRAvg))

#Convert SINR to dB just to see which cluster has bigger SINR    
SINRinDB = []
for i in range(len(SINRAvgPrioritized)):
      SINRinDB.append(10 * math.log(SINRAvgPrioritized[i]))  
       
     
#Centroids - median of clusters
x_clusters_mean = [None] * len(clusters)
y_clusters_mean = [None] * len(clusters)
for i in range(len(clusters)):
    x_clusters_mean[i] = []
    y_clusters_mean[i] = []
    x_clusters_mean[i].append(statistics.mean(x_clusters[i]))
    y_clusters_mean[i].append(statistics.mean(y_clusters[i]))
    
Centroids = list(zip([i[0] for i in x_clusters_mean],[i[0] for i in y_clusters_mean]))


    
#Reorder Centroides based on prioritized AVGSINR
CentroidsPrio = []   
for i in range(len(SINRAvg)):
    index_SAP = np.where(SINRAvg == SINRAvgPrioritized[i] )
#    print(index_SAP[0])
#    print(Centroids[int(index_SAP[0])])
    CentroidsPrio.append(Centroids[int(index_SAP[0])])
    
#for i in CentroidsPrio:
#    print("{} {} ".format(i[0], i[1]))
#centroidsarray = np.asarray(Centroids)
#print(centroidsarray)



#  KNN Implementation for finding the nearest UABS to the X Centroid.
# Create the knn model.
# Look at the five closest neighbors.
if  (CentroidsPrio):
      Kneighbors = 2
      knn = KNeighborsClassifier(n_neighbors= Kneighbors, weights= "distance" , algorithm="auto") #estaba weight="uniform"
      knn.fit(UABSCoordinates,cellid3)
#predict witch UABS will be serving to the X Centroid.
      Knnpredict= knn.predict(CentroidsPrio)
      j=0
      for i in CentroidsPrio:
            print("{} {} {} ".format(i[0], i[1], Knnpredict[j]))
            j+=1 
else:
      for i in CentroidsPrio:
            print("{} {} ".format(i[0], i[1]))

#scores = {}
#scores_list = []
#for k in range(Kneighbors):
#    scores[k] = metrics.accuracy_score(cellid3,Knnpredict)
#    scores_list.append(metrics.accuracy_score(cellid3,Knnpredict))
