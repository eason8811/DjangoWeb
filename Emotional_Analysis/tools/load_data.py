import pandas as pd
import pymysql as pm

class DbProcess:
    db = None
    cur = None

    @classmethod
    def __init__(cls):
        if cls.db is None:
            cls.db = pm.connect(
                host="localhost", user="root", password="123456", db="web_project", port=3306
            )
            print("连接数据库成功")
            cls.cur = cls.db.cursor()

    def get_db(self):
        return self.db

    def load_csv(self, csv_file_path):
        data = pd.read_csv(csv_file_path, index_col=0)

        self.cur.execute("truncate table comment;")
        for i in range(len(data)):
            list = []
            list.append(str(i))
            for j in range(3):
                list.append(str(data.iloc[i, j]))
            self.cur.execute(
                f"INSERT INTO comment VALUES {list[0], list[1], list[2], list[3]}"
            )
            # self.cur.execute(f'INSERT INTO {table_name} VALUES ({i},{data.iloc[i,'comment_text']}, {data.iloc[i,'comment_date']}, {data.iloc[i,'comment_time']})')
            self.db.commit()

if __name__ == '__main__':
    db = DbProcess()
    db.load_csv(f"../output/data_300059.csv")