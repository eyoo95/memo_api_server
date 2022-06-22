from flask_restful import Resource
from flask import request
from mysql.connector.errors import Error
from mysql_connection import get_connection
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector


class MemoListResource(Resource):
    # 메모를 작성하는 API
    @jwt_required()
    def post(self):
        data = request.get_json()

        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query =  '''insert into memo
                        (title, date, memo, user_id)
                        values
                        (%s, %s, %s, %s);'''

            record = (data['title'], data['date'],data['memo'], user_id)

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

    @jwt_required()
    def get(self) :
        # 쿼리 스트링으로 오는 데이터는 아래처럼 처리한다.
        offset = request.args['offset']
        limit = request.args['limit']

        #DB로부터 데이터를 받아서 클라이언트에 보낸다.

        try :
            connection = get_connection()

            user_id = get_jwt_identity()

            query = '''select * 
                    from memo
                    where user_id = %s
                    limit '''+offset+''','''+limit+''';'''

            record = (user_id,)

            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query,record )

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
            return {"error":str(e), 'error_no':20}, 503

        return { "result" : "success",
                "count" : len(result_list),
                "result_list" : result_list} , 200

class MemoInfoResource(Resource):

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

            query = '''update memo
                        set title = %s,
                        date = %s,
                        memo = %s
                        where id = %s and user_id = %s;'''

            record = (data['title'],data['date'],data['memo'], memo_id, user_id)
           
            cursor = connection.cursor(dictionary = True)

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
    @jwt_required()
    def delete(self,memo_id):
        user_id = get_jwt_identity()
        try : 
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''delete from memo
                        where id = %s and user_id = %s;'''

            record = ( memo_id, user_id ) # 튜플형식


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

