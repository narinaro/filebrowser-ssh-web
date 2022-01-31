with open('test') as f:
    lines = f.read()
array = lines.split(';')
response = []

for i in array:
    response.append(i.splitlines())

items = []
baseDir = []
folderName = []
folderWithPath = []
fileName = []
fileWithPath = []
skip = 0

for element in response:
    if skip == 1:
        path = element[1]
        for j in range(2, len(element)):
            curr = path + element[j] 
            items.append(curr)
    else:
        baseDir = element
        skip = 1

for i in items:
    if i[-1] == "/":
        lastOcc = i.rfind(":")
        folderWithPath.append(i[:lastOcc])
        folderName.append(i[lastOcc + 1:])
    else:
        lastOcc = i.rfind(":")
        fileWithPath.append(i[:lastOcc])
        fileName.append(i[lastOcc + 1:])

fileZip = list(zip(fileName, fileWithPath))
folderZip = list(zip(folderName, folderWithPath))

print(fileZip)
print(folderZip)
print(baseDir)

