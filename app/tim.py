import pytz
from datetime import datetime
date_string="2021-07-04T18:33:48+55000.2222"
date_object = datetime.strptime(date_string[:19], "%Y-%m-%dT%H:%M:%S")

t1 = datetime.utcnow().replace(tzinfo=pytz.utc)
t2 = datetime.today()
t3 = datetime.now(pytz.utc)
t4 = date_object.replace(tzinfo=pytz.utc)
tt = t1-t4
print("t1 = ", date_object)
print("t2 = ", tt)
print("Age = ", tt.days, "days and ", int(tt.seconds/3600), "hours ago" )