import os 
import sys


def main():

    filename = sys.argv[1]

    with open(filename,'r') as f:
        buflist = f.read().split('\n')
        rapperlist = []
        for idx, item in enumerate(buflist): 
            try:
                if int(item) < 200:
                    print(f'adding {buflist[idx+3]} to list')
                    rapperlist.append(buflist[idx+3])

            except: 
                pass 


    print(rapperlist)
    return rapperlist



if __name__ == "__main__":
    main()
