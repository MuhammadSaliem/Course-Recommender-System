from sklearn.metrics.pairwise import cosine_similarity


def similar_course_list(course_id, n_courses, df_courses, df_norm):
    id_=df_courses[df_courses['id']==course_id].index.values
    title=df_courses[df_courses['id']==course_id]['published_title']
    df_result= df_courses.copy()

    df_result['cosine_similarity'] = cosine_similarity(df_norm.values, df_norm.loc[id_].values.reshape(1, -1))  
    df_result= df_result.sort_values('cosine_similarity', ascending=False).reset_index(drop=True)
    return title, df_result.iloc[1:n_courses+1][['published_title', 'cosine_similarity','image', 'instructor', 'price']]

def recommend_for_user(n_courses, taken_courses, df_courses, df_norm):
    n_courses += 1
    #list_courses= taken_courses
    #numOfCourses =len(taken_courses)
    #index_courses=df_courses[df_courses['id'].isin(taken_courses)].index

    if len(taken_courses) >= 1:
        #n_courses=n_courses+1
        tmp_dataFrame =df_courses.copy()
        for i, course_id in enumerate(taken_courses):
            #id_=df_courses[df_courses['id']==course_id].index.values
            #X = df_norm.values
            #Y = df_norm.loc[id_].values.reshape(1, -1)
            tmp_dataFrame[i] = cosine_similarity(df_norm.values, df_norm.loc[df_courses[df_courses['id']==course_id].index.values].values.reshape(1, -1))

        tmp_dataFrame['avg_cos_sim']= tmp_dataFrame.iloc[:,-len(taken_courses):].mean(axis=1).values
        #df_temp['avg_cos_sim']=temp_avg
        tmp_dataFrame.drop(index=df_courses[df_courses['id'].isin(taken_courses)].index, inplace=True)
        tmp_dataFrame =tmp_dataFrame.sort_values('avg_cos_sim', ascending=False).reset_index(drop=True)
        return tmp_dataFrame #return df_temp for Flask API

        
