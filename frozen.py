from transgender import TG
import datetime

if __name__ == '__main__':
    #TG.frozen()
    start = datetime.datetime.now()
    for i in range(10):
        print(TG.answer("安安"))
    print('take {} sec'.format(datetime.datetime.now() - start))
