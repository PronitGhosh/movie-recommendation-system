import numpy as np
import requests
import pandas as pd
from django.shortcuts import render
from sklearn.metrics.pairwise import cosine_similarity
def get_movie_poster(movie_title):
    url=f'https://api.themoviedb.org/3/search/movie?api_key=6254bd771d79df7434bd6538077de092&query={movie_title}'
    response=requests.get(url)
    data=response.json()
    if data.get("results"):
        movie=data["results"][0]
        poster_path=movie.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return None
def recommend(movie_name,pt,similarities_scores):
    index=np.where(pt.index==movie_name)[0][0]
    similarities= sorted(list(enumerate(similarities_scores[index])),key=lambda x:x[1],reverse=True)[1:6]
    list2=[]
    for i in similarities:
        list2.append(pt.index[i[0]])
    return list2
def home(request):
    credit=pd.read_csv(r"C:\\Users\\proni\\Downloads\\Dataset.csv")
    movies=pd.read_csv(r"C:\\Users\\proni\\Downloads\\Movie_Id_Titles.csv")
    df=movies.merge(credit,on="item_id")
    df=df.drop(['timestamp'],axis=1)
    num_df=df.groupby('title').count()['rating'].reset_index()
    num_df.rename(columns={'rating':'num_rating'},inplace=True)
    avg_df=df.groupby('title').mean()['rating'].reset_index()
    avg_df.rename(columns={'rating':'avg_rating'},inplace=True)
    popular_df=num_df.merge(avg_df,on='title')
    latest=popular_df.merge(movies,on='title')
    latest=latest[latest['num_rating']>=250].sort_values('avg_rating',ascending=False)
    list1=[]
    context_list=[]
    for index,row in latest.iterrows():
        title=row["title"]
        votes=row["num_rating"]
        rating=row["avg_rating"]
        rating=round(rating,1)
        poster_url=get_movie_poster(title)
        if poster_url==None:
              latest= latest[latest['title'] != title]
              df = df[df['title'] != title]
              
        else:
         context={'title':title,'poster_url':poster_url,"votes":votes,"rating":rating}
         context_list.append(context)
    return render(request,"home.html",{"context_list":context_list})
def predict(request):
    return render(request,"predict.html")
def result(request):
    credit=pd.read_csv(r"C:\\Users\\proni\\Downloads\\Dataset.csv")
    movies=pd.read_csv(r"C:\\Users\\proni\\Downloads\\Movie_Id_Titles.csv")
    df=movies.merge(credit,on="item_id")
    df=df.drop(['timestamp'],axis=1)
    x=df.groupby('user_id').count()['rating']>200
    educated_users=x[x].index
    filtered_rating=df[df['user_id'].isin(educated_users)]
    y=filtered_rating.groupby("title").count()['rating']>=50
    famous_movies=y[y].index
    final_rating=filtered_rating[filtered_rating['title'].isin(famous_movies)]
    pt=final_rating.pivot_table(index="title",columns="user_id",values='rating')
    pt.fillna(0,inplace=True)
    similarities_scores=cosine_similarity(pt)
    movie=request.GET['movie-name']
    list1=[]
    list1=recommend(movie,pt,similarities_scores)
    context_list=[]
    for i in list1:
         poster_url=get_movie_poster(i)
         if poster_url!=None:
          context={"poster_url":poster_url,"title":i}
          context_list.append(context)
    return render(request,"predict.html",{"context_list":context_list})