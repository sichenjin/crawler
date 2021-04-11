
file1 = open('./crawler/meishijie.txt', 'r')
Lines = file1.readlines()

for line in Lines:
    try:
        steps = line['步骤']
        imgs = line['图片']
        line['步骤图']=[]
        if(len(steps) == len(imgs)):
            for i in range(len(steps)):
                line['步骤图'].append({
                    '步骤':steps[i],
                    '图':imgs[i]
                })
        else: continue 
    except: continue 

file1.close()

file2 = open('meishijie_buzhoutu.txt', 'w')
print(Lines[0])
file1.writelines((Lines))
file2.close()

