from app.history import get_history,add_message,delete_history

print(add_message(1,"user","这是一条测试信息111"))
print(add_message(2,"user","这是一条测试信息222"))
print(add_message(3,"assianst","这是一条测试信息333"))
delete_history(3)
print(get_history(3))


