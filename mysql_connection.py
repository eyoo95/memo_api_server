import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host = 'yh-db.c3pciphtm1bo.ap-northeast-2.rds.amazonaws.com',  # sql 호스트네임 작성
        database = 'memo_db',
        user = 'memo_user',  # SQL 에서 작성한 레시피 앱 사용자 계정
        password = 'memo1234'
    )
    return connection