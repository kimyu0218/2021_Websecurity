import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.run(host='0.0.0.0', debug = True)

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/pdf_parsing', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files
        filenames = []
        for file in files.to_dict(flat=False)['file']:
            filenames.append(file.filename)
            file.save('/'+secure_filename(file.filename))
        return render_template('result.html', result=filenames, files=filenames)
        '''
        os.system("""ls -d /var/www/html/files/* > ~/hidost/build/tpdfs.txt &&
                    cd ~/hidost/build/ && 
                    ./src/cacher -i tpdfs.txt --compact --values -c cache/ -t10 -m256 && 
                    find cache -name '*.pdf' -not -empty > cached-tpdfs.txt &&
                    cat cached-bpdfs.txt cached-mpdfs.txt cached-tpdfs.txt > cached-pdfs.txt &&
                    cat cached-bpdfs.txt cached-tpdfs.txt > cached_benign_test.txt &&
                    ./src/pathcount -i cached-pdfs.txt -o pathcounts.bin && 
                    ./src/feat-select -i pathcounts.bin -o features.nppf -m1000 && 
                    ./src/feat-extract -b cached_benign_test.txt -m cached-mpdfs.txt -f features.nppf --values -o data.libsvm &&
                    cat features.nppf | wc -l > ~/feature_count.txt &&
                    ls /var/www/html/files/* | wc -l > ~/upload_count.txt""")
        f = open("~/feature_count.txt", "r")
        feature_line = int(f.read())
        f.close()

        input_f = open('~/hidost/build/data.libsvm', 'r')
        output_f = open('./output.csv', 'w')

        lines = input_f.readlines()
        for line in lines:
            minus_list = [-1] * (feature_line - 1)
            
            l = line.split(' #')[0]
            l = l.split(' ')
            file_name = line.split(' #')[1].strip('\n')
            
            for i in range(len(l)):
                if i != 0:
                    key = int(l[i].split(':')[0])
                    val = float(l[i].split(':')[1])
                    minus_list[key-1]=val
            if int(l[0]) == 1:
                mb = 'M'
            else:
                mb = 'B'
            
            result_string=mb+', '+str(minus_list).strip('[]')+', '+file_name
            output_f.write(result_string)
        input_f.close()
        output_f.close()

        data = pd.read_csv("./output.csv", header=None, error_bad_lines=False)

        data = data.drop(data.columns[-1], axis=1) # 필요 없는 데이터 제거 (파일의 맨 마지막에 파일 경로 저장)
        data_drop = data.drop(0, axis=1) # 파일 라벨 제거
        Y = data[0] # 0번째 컬럼에 라벨 저장되어 있음

        datas = pd.DataFrame(data_drop.iloc[:,0:])
        datas.columns = data_drop.iloc[:,0:].columns

        X = datas.values

        f = open("~/upload_count.txt", "r")
        upload_count = int(f.read())
        f.close()

        x_train, x_test, y_train, y_test = train_test_split(X,Y,test_size=upload_count/len(X),random_state=0)
        y_train = y_train.to_numpy()
        y_test = y_test.to_numpy() 

        rfc = RandomForestClassifier(random_state=0)
        rfc.fit(x_train, y_train)

        predict = rfc.predict(x_test)
        score = accuracy_score(y_test, predict)
        print("Acc: " + str(score))
        print("Predict: " + str(predict))

        return render_template('result.html', value=predict.tolist(), files=filenames)
'''