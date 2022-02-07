import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
            file.save('/var/www/html/files/'+secure_filename(file.filename))

        os.system("""sudo ls -d /var/www/html/files/* > ~/hidost/build/tpdfs.txt &&
                    cd ~/hidost/build/ && 
                    sudo mkdir cache &&
                    sudo ./src/cacher -i tpdfs.txt --compact --values -c cache/ -t10 -m256 && 
                    sudo find cache -name '*.pdf' -not -empty > cached-tpdfs.txt &&
                    cat cached-bpdfs.txt cached-mpdfs.txt cached-tpdfs.txt > cached-pdfs.txt &&
                    cat cached-bpdfs.txt cached-tpdfs.txt > cached_benign_test.txt &&
                    ./src/pathcount -i cached-pdfs.txt -o pathcounts.bin && 
                    ./src/feat-select -i pathcounts.bin -o features.nppf -m1000 && 
                    ./src/feat-extract -b cached_benign_test.txt -m cached-mpdfs.txt -f features.nppf --values -o data.libsvm &&
                    sudo cat features.nppf | wc -l > ~/feature_count.txt &&
                    sudo ls /var/www/html/files/* | wc -l > ~/upload_count.txt &&
                    sudo find /var/www/html/files -name '*.pdf' -exec rm {} \; &&
                    sudo rm -r cache
""")
        f = open("/home/kimyujeong/feature_count.txt", "r")
        feature_line = int(f.read())
        f.close()

        input_f = open('/home/kimyujeong/hidost/build/data.libsvm', 'r')
        output_f = open('/home/kimyujeong/hidost/build/output.csv', 'w')

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
            
            result_string=mb+', '+str(minus_list).strip('[]')+', '+file_name+"\n"
            output_f.write(result_string)
        input_f.close()
        output_f.close()

        data = pd.read_csv("/home/kimyujeong/hidost/build/output.csv", header=None, error_bad_lines=False)

        X = data.drop(0, axis=1)
        Y = data[0]

        X = X.drop(X.columns[-1], axis=1)

        f = open("/home/kimyujeong/upload_count.txt", "r")
        upload_count = int(f.read())
        f.close()
   
        x = X.iloc[:-upload_count]
        y = Y[:-upload_count]
        test = X.iloc[-upload_count:]

        x = x.to_numpy()
        y = y.to_numpy()

        x_train, x_test, y_train, y_test = train_test_split(x,y,test_size=0.1,random_state=0)

        rfc = RandomForestClassifier(random_state=0)
        rfc.fit(x_train, y_train)

        score = accuracy_score(y_test, rfc.predict(x_test))
        print(score)

        predict = rfc.predict(test)

        return render_template('result.html', result=predict, files=filenames)

app.run(host='0.0.0.0', debug = True)
