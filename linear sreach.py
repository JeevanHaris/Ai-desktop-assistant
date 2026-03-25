def linear_sreach(array,num):
    length=len(array)-1
    for i in range(length):
        if array[i]==num:
            return i
    return -1

arr=[1,2,3,4,5,6,7,8]
key=6
result=linear_sreach(arr,key)
if result !=-1:
    print("element found at index",result)
else:
    print("not found")
