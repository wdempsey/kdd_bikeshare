import os
import psycopg2
import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
import pickle
import random
import math
from datetime import *
import pytz
from dateutil.relativedelta import *
from dateutil.parser import parse
import calendar
from poisson_data_extract import *
from poisson_fit import *


def load_poisson_result(station_id, include_rebalance = False):
    tag = "rebalanced"
    if (include_rebalance == False):
        tag = "notrebalanced"
    temp = pickle.load(open("/Users/walterdempsey/Documents/github/kdd_bikeshare/model/pickles/poisson_results_%s_%s.p" % (station_id,tag), "rb"))
    return (dict(params=temp[0]), dict(params=temp[1]))

##  Pull the Estimated Mean at Month, Time, Weekday Triple
##  Create A List for All Stations and Their Corresponding Ids

cluster_ids = [129, 130, 131, 134, 138, 139, 140, 156, 157, 158, 160, 161, 165, 166, 167, 170, 172, 173, 174, 175, 176, 177, 180, 181, 182, 201, 202, 203, 211, 212, 221, 245]

month = 5
time = 24
weekday = 1

def mean_params(cluster_ids):
    #  Pulls the rate parameters for the half-hour interval for each 
    #  Station in the Cluster (both arrival and departure)
    station_ids =[]
    for id in cluster_ids:
        station_level_models = load_poisson_result(id)
    
        arrival_lambda = lambda_calc(month, time, weekday, station_level_models[0])
        departure_lambda = lambda_calc(month, time, weekday, station_level_models[1])
        lambda_t = [lambda_t,arrival_lambda,departure_lambda]
        station_ids.append(id)
        station_ids.append(id)

    return([lambda_t,station_ids,error])


## Given Two Stations We Compute the L2-Distance : Requires the Table Jette Gave Me
summary_table = pd.read_table('/Users/walterdempsey/Documents/github/kdd_bikeshare/data/stations_with_cluster.csv', header = 0, delimiter = " ")

def distance(station_1, station_2):
    # Computes and Returns the L2-Distance Between Stations
    summary_station1 = summary_table[summary_table.id == station_1]
    summary_station2 = summary_table[summary_table.id == station_2]
    distance = (float(summary_station1.latitude) - float(summary_station2.latitude))**2 + (float(summary_station1.longitude) - float(summary_station2.longitude))**2
    return(distance)


def Covariance(cluster_ids, sigma_sq_error, sigma_sq_station, sigma_sq_spatial, range_parameter):
    # Computes the Covariance Given the Var Components Estimates
    num_clust = len(cluster_ids)
    Spat_Cov = np.zeros((num_clust,num_clust))
    Station_Cov = np.zeros((num_clust,num_clust))
    Measurement_Error = sigma_sq_error*np.identity(num_clust)
    for i in range(0,num_clust):
        for j in range(0,num_clust):
            Spat_Cov[i,j] = sigma_sq_spatial*np.exp(-distance(cluster_ids[i], cluster_ids[j])/range_parameter)
            Station_Cov[i,j] = sigma_sq_station*(cluster_ids[i]==cluster_ids[j])
    return(Measurement_Error+Station_Cov+Spat_Cov)


## Joint Simulation ##

def JointSim(mean_rate, Sigma):
    z = [0]*len(mean)
    for i in range(0,len(mean_rate)):
        z[i] = np.random.normal(loc = mean_rate[i])

    Chol = np.linalg.cholesky(Sigma)

    rand_lambda = np.exp(np.dot(Chol,z))
    Y = [0]*len(rand_lambda)

    for i in range(0,len(rand_lambda)):
        Y[i] = np.random.poisson(rand_lambda[i])

    return [rand_lambda, Y]

mean_rate, station_ids, error = mean_params(cluster_ids)
Sigma = Covariance(cluster_ids, 0.5,0.25,0.25, 0.0007)

output = JointSim(mean_rate,Sigma)

## Build Database for Specific Month, Time, Weekday Triple
## For All Stations in Cluster

# Provided By Vidhur
# Should Produce Observations to Be Used in Calculations


## Conditional Simulation Given Data and Mean Parameters ##

def un_normalized_log_density(rand_lambda, observations, mean_rate,Sigma):
    logdens = 0
    for i in range(0,len(rand_lambda)):
        logdens = logdens + (observations[i])*np.log(rand_lambda[i]) - rand_lambda[i]
    diff = (np.log(rand_lambda) - mean_rate)
    return(dens+(-np.dot(np.dot(diff, np.linalg.inv(Sigma)),diff)/2))

def inv_information(rand_lambda, Sigma):
    return(np.linalg.inv((np.diag(rand_lambda)+np.linalg.inv(Sigma))))

def proposal(given_lambda, c, Sigma):
    new_lambda = [0]*len(given_lambda)
    for i in range(0,len(given_lambda)):
        log_lambda[i] = np.random.normal(loc = np.log(rand_lambda[i]))
    # h_lambda = 2.38**2
    proposal_variance = c*inv_information(given_lambda, Sigma)
    prop_Chol = np.linalg.cholesky(proposal_variance)
    proposal_lambda = np.exp(np.dot(prop_Chol,log_lambda))
    return(proposal_lambda)

def log_proposal_distribution(prop_lambda, given_lambda,Sigma):
    logdiff = (np.log(prop_lambda) - np.log(given_lambda))
    term2 = -np.dot(np.dot(logdiff ,np.linalg.inv(Sigma)),logdiff)/2
    term1 = -np.linalg.slogdet(inv_information(prop_lambda,Sigma))[1]/2
    return(term1+term2)


def next_lambda(given_lambda,c, obs, mean_rate, Sigma):
    prop_lambda = proposal(rand_lambda,c,Sigma)
    term_A = log_proposal_distribution(prop_lambda,given_lambda,Sigma)-log_proposal_distribution(given_lambda,prop_lambda,Sigma)
    term_B = un_normalized_log_density(prop_lambda, obs, mean_rate,Sigma)-un_normalized_log_density(given_lambda, rand_obs, mean_rate,Sigma)
    prop = min(1,np.exp(term_A + term_B))
    s = np.random.uniform(0,1,1)
    if s < prop:
        return(prop_lambda)
    else:
        return(given_lambda)


def mcmc_run(initial_lambda, trials, obs, mean_rate,Sigma):
    mcmc_results =[]
    current_lambda = initial_lambda
    for i in range(0,trials):
        new_lambda = next_lambda(current_lambda,0.01, obs, mean_rate, Sigma)    
        mcmc_results.append(new_lambda)
        current_lambda = new_lambda
    return(mcmc_results)
