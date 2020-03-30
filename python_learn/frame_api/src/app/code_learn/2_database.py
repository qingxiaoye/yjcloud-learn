from sqlalchemy import create_engine
#链接数据库
engine = create_engine('mysql+cymysql://root:yjyjs123@localhost:3306/yj_speech_qia')
# engine.execute("insert into test1(id,name,salary) values(1,'zs',88888)")
#查看数据
result = engine.execute('select * from qi_info_user')
rows = result.fetchall()


