# 데이터베이스에 접속해서, 데이터 처리하는 테스트 코드
from flask import Flask, jsonify, request
from http import HTTPStatus
from flask_jwt_extended import JWTManager
from flask_restful import Api
import mysql.connector
from mysql_connection import get_connection

title = '식사'
date = '2022-05-06'
memo = '식사를 합시다.'

try :

    # 데이터 insert 
    # 1. DB에 연결
    connection = get_connection()

    # 2. 쿼리문 만들기
    query = '''insert into memo
                (title, date, memo)
                values
                (%s, %s, %s);'''

    record = (title, date, memo ) # 튜플형식
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