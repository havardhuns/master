



def deletedb():
    for i in range(100000, 700001, 100000):
        for j in range(1,4):
            collection = db[f'linked-inputs-{i}-{j}']
            collection.drop()