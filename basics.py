name = "小明"
age =  25
is_ready = True

print (f"我叫{name}, 今年{age}岁")

skills = ["Java", "Solace", "Splunk"]
skills.append("Python")

print(skills)
print(skills[0])
print(skills[-1])

person = {
    "name": "小明",
    "age": 25,
    "skills": ["java", "Solace", "Splunk"]
}
print(person["name"])   
print(person.get("salary", "没有这个key"))

def greet(name, greeting="hello"):
    return f"{greeting}，{name}！"

print(greet("小明"))
print(greet("小红", "早上好"))

for skill in skills:
    print(f"技能：{skill}")

score = 85
if score >=90:
    print("A")
elif score >=60:
    print("及格")
else:
    print("不及格")

try:
    result = 10/0
except ZeroDivisionError as e:
    print(f"出错了: {e}")