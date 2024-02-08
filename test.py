a = int(input())

col = 0

while a != 0:
    
    
    if(a % 5 == 0 or a % 9 == 0):
        col += 1

    a = int(input())
print(col)