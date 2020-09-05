DATABASE = 'blog_db'

TABLES = dict()
TABLES['USER'] = ("CREATE TABLE USER(USER_ID INT(3) PRIMARY KEY AUTO_INCREMENT,"
                  " USER_NAME VARCHAR(20) UNIQUE"
                  " NOT NULL, PASSWORD VARCHAR(20) NOT NULL);"
                  )


TABLES['POST'] = ("CREATE POST(POST_ID INT(3) PRIMARY KEY AUTO_INCREMENT,"
                  " TITLE VARCHAR(50) NOT NULL,"
                  " BODY VARCHAR(500),"
                  " AUTHOR_ID INT(3) NOT NULL,"
                  "CREATED DATETIME NOT NULL DEFAULT NOW(),"
                  "FOREIGN KEY(AUTHOR_ID) REFERENCES USER(USER_ID));"
                  )

