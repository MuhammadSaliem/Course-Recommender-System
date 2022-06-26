#import requests
#import ast
#import re
#import numpy as np
#import pandas as pd
#import matplotlib.pyplot as plt
#import seaborn as sns
#from wordcloud import WordCloud
#from nltk.tokenize import word_tokenize
#from nltk.stem import SnowballStemmer
#from operator import itemgetter
#from collections import Counter
#import matplotlib
#import squarify
#from sklearn.cluster import KMeans
#from scipy.spatial.distance import pdist
#from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
#from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
#from sklearn.metrics import euclidean_distances
#from sklearn.preprocessing import StandardScaler




def recommend_courses(course_id, n_courses, df_courses, df_norm):
    n_courses=n_courses+1
    id_=df_courses[df_courses['id']==course_id].index.values
    title=df_courses[df_courses['id']==course_id]['published_title']
    X = df_norm.values
    Y = df_norm.loc[id_].values.reshape(1, -1)
    cos_sim = cosine_similarity(X, Y)
    df_sorted=df_courses.copy()
    df_sorted['cosine_similarity'] = cos_sim
    df_sorted=df_sorted.sort_values('cosine_similarity', ascending=False).reset_index(drop=True)

    return title, df_sorted.iloc[1:n_courses][['published_title', 'cosine_similarity','image', 'instructor', 'price']]

def recommend_for_user(user_name, n_courses, taken_courses, df_courses, df_norm):
    list_courses= taken_courses
    len_courses=len(list_courses)
    index_courses=df_courses[df_courses['id'].isin(list_courses)].index
    for course_id in list_courses:
        title, df_recommend= recommend_courses(course_id, n_courses, df_courses, df_norm)
        print('The following courses are recommended after taking the course {} with the id {}:'
          .format(title.values[0],course_id))
        print(df_recommend)
        print()
    if len_courses>1:
        n_courses=n_courses+1
        df_temp=df_courses.copy()
        for i, course_id in enumerate(list_courses):
            id_=df_courses[df_courses['id']==course_id].index.values
            X = df_norm.values
            Y = df_norm.loc[id_].values.reshape(1, -1)
            cos_sim = cosine_similarity(X, Y)
            df_temp[i] = cos_sim
        temp_avg=df_temp.iloc[:,-len_courses:].mean(axis=1).values
        df_temp['avg_cos_sim']=temp_avg
        df_temp.drop(index=index_courses, inplace=True)
        df_temp=df_temp.sort_values('avg_cos_sim', ascending=False).reset_index(drop=True)
        print('The following courses are recommended after all taken courses:')
        print(df_temp.iloc[1:n_courses][['published_title', 'avg_cos_sim', 'image', 'instructor', 'price']])
        return df_temp #return df_temp for Flask API
