from ast import Delete
from http import HTTPStatus
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector

class MemoResource(Resource):
    # 클라이언트로부터 /memo/3 같이 경로처리
    # 숫자가 바뀌므로 면수로 처리한다.
    def get(self,memo_id):

        # DB에서 memo_id 에 들어있는 값 데이터를 select한다.
        try :
            connection = get_connection()

            query = '''select *
                        from memo
                        where id = %s ;'''

            record = (memo_id,)

            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query,record )

            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            result_list = cursor.fetchall()

            print(result_list)
            
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

        

        return {'result' : 'success' ,
                'info' : result_list[0]} ,200

    # 데이터를 업데이트하는 API는 PUT 함수를 사용한다.
    @jwt_required()
    def put(self, memo_id) :

        # body에서 전달된 데이터를 처리
        data = request.get_json()

        user_id = get_jwt_identity()

        # 디비 업데이트 실행코드
        try :
            # 데이터 업데이트 
            # 1. DB에 연결
            connection = get_connection()

            ### 먼저 memo_id 에 들어있는 user_id가
            ### 이 사람인지 먼저 확인한다.

            query = '''select user_id 
                        from memo
                        where id = %s;'''
            record = (memo_id, )
           
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            if len(result_list) == 0 :
                cursor.close()
                connection.close()
                return {'error' : '레시피 아이디가 잘못되었습니다.'}, 400

            memo = result_list[0]

            if memo['user_id'] != user_id :
                cursor.close()
                connection.close()
                return {'error' : '남의 레시피를 수정할수 없습니다.'}, 401


            # 2. 쿼리문 만들기
            query = '''update memo
                    set name = %s , description = %s , 
                    cook_time = %s , 
                    directions = %s
                    where id = %s ;'''
            
            record = (data['name'], data['description'],
                        data['cook_time'], data['directions'],
                        memo_id )

            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 503

        return {'result' :'success'}, 200

    # 삭제하는 delete함수
    def delete(self,memo_id ):
        try : 
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''delete from memo
                        where id = %s;'''

            record = ( memo_id, ) # 튜플형식


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

