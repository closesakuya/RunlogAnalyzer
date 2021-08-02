import sqlite3
import re
import os

PT = re.compile(r"(\d+)\s+\d+\s+\d+\s+[0-9A-F\s]{17}(.*)")


def gen_sql_from_line(src: str) -> str:
    result = re.search(PT, src)
    if result and result.groups().__len__() >= 2:
        dates = result.groups()[0]
        logs = result.groups()[1]
        if dates.__len__() < 14:
            return ""
        return """INSERT INTO device_runlog_data (uuid,log_time,operate_user,duration,operation_desc) VALUES 
        ('', '{0}-{1}-{2} {3}:{4}:{5}', '1', '', '[运行] {6}')""".\
            format(dates[0:4], dates[4:6], dates[6:8], dates[8:10], dates[10:12], dates[12:14], logs.strip("\n"))

    return ""

def gen_select_sql_from_line(src: str) -> str:
    result = re.search(PT, src)
    if result and result.groups().__len__() >= 2:
        dates = result.groups()[0]
        logs = result.groups()[1]
        if dates.__len__() < 14:
            return ""
        return """SELECT COUNT(*) FROM device_runlog_data WHERE log_time = '{0}-{1}-{2} {3}:{4}:{5}' and 
        operation_desc = '[运行] {6}'""".\
            format(dates[0:4], dates[4:6], dates[6:8], dates[8:10], dates[10:12], dates[12:14], logs.strip("\n"))
    return ""


def r40log_to_db(log_file: [str], db_file: str, sel_before_insert: bool = False):
    if not os.path.exists(db_file):
        print("not found db file: {0}".format(db_file))
        return
    conn = sqlite3.connect(db_file)
    if not conn:
        print("open db {0} failed !".format(db_file))
    cur = conn.cursor()
    line_cnt = 0
    for item in log_file:
        if not os.path.exists(item):
            print("not found {0}".format(item))
            continue
        with open(item, 'r') as f:
            print("do txt: {0}".format(item))
            for line in f.readlines():
                line = line.strip('\n')
                line = bytes(line.encode('utf-8')).strip(b'\x00').decode('utf-8')
                sql = gen_sql_from_line(line)
                sql_sel = gen_select_sql_from_line(line)
                if sql:
                    # 查找是否已存在
                    res = cur.execute(sql_sel)
                    # print(res.fetchone()[0])
                    if sel_before_insert and res.arraysize >= 1 and int(res.fetchone()[0]) >= 1:
                        for r in res:
                            print(r)
                        print("find duplicate in ", sql_sel)
                        continue
                    # print(sql)
                    line_cnt += 1
                    cur.execute(sql)


    conn.commit()
    conn.close()
    print("insert  to db {0} lines: {1} successful".format(db_file, line_cnt))


if __name__ == "__main__":
    cur_dir = os.getcwd()
    F = []
    for item in os.listdir(cur_dir):
        if item.lower().endswith(".txt"):
            F.append(item)
    r40log_to_db(F, "wruntime.db", False)
    a = input("\n完成，任意键退出...\n")