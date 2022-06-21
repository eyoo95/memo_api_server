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


    def get(self) :
        # 쿼리 스트링으로 오는 데이터는 아래처럼 처리한다.
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        #DB로부터 데이터를 받아서 클라이언트에 보낸다.

        try :
            connection = get_connection()

            query = '''select * 
                    from memo
                    limit '''+offset+''','''+limit+''';'''

            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query )

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

        return { "result" : "success",
                "count" : len(result_list),
                "result_list" : result_list} , 200

