dict1={"a":2, "b": 4, "c": 5, "d":6}
dict2={'e': 1, 'f': 3, 'g': 7, 'h': 8}

merger_dict = {**{ k: v for k, v in dict1.items() if v in [2,4,1] }, **{k: v for k, v in dict2.items() if v in [2,4,1]}}
print(merger_dict)

#a= 2+2
#print(_)

x,_,y = (1, 'aaa', 4)
print(x,y)

ids=[1,2,3,4]
names = ['jane', 'jeff','bob','lisa'] 
grades =['A', 'B','A','C']
ages= [22,31,35,28]

paired = zip(names, ages)
print(paired)
print(type(paired))
paired = list(zip(names,ages))
print(paired)
print(type(names))

paired = dict(zip(ids,zip(names,grades)))
#paired = zip(ids,names,grades)
print(type(paired))
print(paired)

data=[]
for i in range(6):
    x=lambda a, i =i*2: i*a
    data.append(x)

#print(data[1](3,88))
print([(f, f(3)) for f in data]) 
#print(data)

for i in data:
    print(i)
print(data[1])

def convert(x):
    data = []
    for i in range(6):
        i *= 2
        data.append(i*x)
    return data