from http import HTTPStatus
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector
from email_validator import validate_email, EmailNotValidError
from utils import hash_password, check_password
import datetime

class MemoFollowResource(Resource):
    # 팔로우하는 API
    @jwt_required()
    def post(self, follower_id):
        data = request.get_json()

        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query =  '''insert into follow
                        ( followee_id, follower_id)
                        value
                        (%s,%s);'''

            record = (data['followee_id'], user_id)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            print (e)
            cursor.close()
            connection.close()
            return {'error':str(e)} , 503
        
        return {'result': 'success'}, 200

class MemoListFollowResource(Resource):
    @jwt_required()
    def get(self) :

        connection = get_connection()

        user_id = get_jwt_identity()
        # 디비로부터 데이터를 받아서, 클라이언트에 보내준다.
        try :
            # 데이터 insert
            # 1. DB에 연결
            
            # 2. 쿼리문 만들기
            query = '''select m.title, m.date, m.memo, m.created_at, m.updated_at
                        from memo m
                        join follow f
                        on m.user_id = f.follower_id
                        where follower_id = %s;'''                 
            record = (user_id, )

            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query, record)

            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            result_list = cursor.fetchall()

            
            # 중요! DB 에서 가져온 timestamp는 파이썬의 datetime으로 자동 변경된다.
            # 문제는 이 데이터를 json.으로 바로 보낼수 없으므로 문자열로 바꿔서 다시 저장해서 보낸다.

            i = 0
            for record in result_list:

                result_list[i]['created_at'] = record['created_at'].isoformat()
                result_list[i]['updated_at'] = record['updated_at'].isoformat()
                result_list[i]['date'] = record['date'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e)}, 503

        return { "result" : "success",
                "count" : len(result_list),
                "result_list" : result_list} , 200

class MemoDeleteFollowResource(Resource):
    def delete(self,follower_id ):
        data = request.get_json()
        try : 
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''delete from follow
                        where followee_id = %s and follower_id = %s;'''

            record = ( data['followee_id'], follower_id) # 튜플형식


            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record )

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error':str(e)}, 503

        return {'result': 'success'} , 200