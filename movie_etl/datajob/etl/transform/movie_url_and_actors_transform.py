from pyspark.sql.functions import col
import pandas as pd
from infra.jdbc import DataWarehouse, save_data
from infra.spark_session import get_spark_session
from infra.util import get_movie_codes


class MovieUrlAndActorsTransformer:

    @classmethod
    def transform(cls):
        movie_codes, movie_names = get_movie_codes()

        for movie_code in movie_codes:
            try : 
                movie = cls.__load_json(movie_code)
                items = cls.__create_dataframe(movie)
                cls.__save_actors(movie_code, items)
                cls.__save_link(movie_code, items)
            except :
                print('empty dataset')

    @classmethod
    def __save_link(cls, movie_code, items):
        try:
            link_df = cls.__generate_link_df(movie_code, items)
            link_df = get_spark_session().createDataFrame(link_df)
            save_data(DataWarehouse, link_df, 'MOVIE_URL')
        except:
            print('save_link error')

    @classmethod
    def __save_actors(cls, movie_code, items):
        try:
            actors_df = cls.__generate_actors_df(movie_code, items)
            actors_df = get_spark_session().createDataFrame(actors_df)
            save_data(DataWarehouse, actors_df, 'ACTORS')
        except:
            print('save_actors error')

    @classmethod
    def __generate_link_df(cls, movie_code, items):
        link = items.link
        link_df = pd.DataFrame({
            'MOVIE_CODE': [movie_code],
            'URL': [link]
        })
        return link_df

    @classmethod
    def __generate_actors_df(cls, movie_code, items):
        actors = items.actor
        actors = actors.split('|')
        actors = actors[:-1]

        movie_codes = []
        for ac in actors:
            movie_codes.append(movie_code)

        actors_df = pd.DataFrame({
            'MOVIE_CODE': movie_codes,
            'ACTOR_NAME': actors
        })

        return actors_df

    @classmethod
    def __create_dataframe(cls, movie):
        items = get_spark_session().createDataFrame(movie['items'])
        items = items['actor', 'link', 'title'].first()
        print(items)
        return items

    @classmethod
    def __load_json(cls, movie_code):
        path = '/movie/naver_search_movie/naver_search_movie_' + movie_code + '.json'
        movie = get_spark_session().read.option(
            "multiline", "true").json(path, encoding='UTF-8').first()

        return movie
