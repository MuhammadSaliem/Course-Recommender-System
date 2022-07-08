from sklearn.metrics.pairwise import cosine_similarity


def similar_course_list(course_id, n_courses, df_courses, df_norm):
    id_=df_courses[df_courses['id']==course_id].index.values
    title=df_courses[df_courses['id']==course_id]['published_title']
    df_result= df_courses.copy()

    df_result['cosine_similarity'] = cosine_similarity(df_norm.values, df_norm.loc[id_].values.reshape(1, -1))  
    df_result= df_result.sort_values('cosine_similarity', ascending=False).reset_index(drop=True)
    return title, df_result.iloc[1:n_courses+1][['published_title', 'cosine_similarity','image', 'instructor', 'price']]

def recommend_for_user(user_name, n_courses, taken_courses, df_courses, df_norm):
    list_courses= taken_courses
    len_courses=len(list_courses)
    index_courses=df_courses[df_courses['id'].isin(list_courses)].index
    for course_id in list_courses:
        title, df_recommend= similar_course_list(course_id, n_courses, df_courses, df_norm)
        print('The following courses are recommended after taking the course {} with the id {}:'
          .format(title.values[0],course_id))
        print(df_recommend)
        print()
    if len_courses>0:
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

        
