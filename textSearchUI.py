import os

import flask
from flask import Flask
from flask import render_template, request, send_from_directory
import json
app = Flask(__name__)
import requests
from nltk.stem import PorterStemmer
import re
from flask import Markup
ps = PorterStemmer()
from stop_words import get_stop_words

stop_words = get_stop_words('english')
@app.route('/upload/<filename>')
def send_image(filename):
    print("hi")
    print(filename)
    return send_from_directory("imageRenamed",filename=filename+".jpg")

@app.route('/')
def hello_world():

    return render_template('textSearch.html')



def checkDuplicateDocumentAndReturnIt(resultData,documentIdData):
    returnData=[]
    for result in resultData:
        if (result.get('document_id') == documentIdData):
            returnData.append(documentIdData)
            returnData.append(result)
    return returnData

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
            contentOfIDF = open('TF_IDF4.txt', 'r').read()
            detailsOfAllData = json.loads(contentOfIDF.lower())
            result = []
            try:
                text = request.form.get("textSearch").lower()
                splitTextArray = text.split(' ')
                print(splitTextArray)
                for i in splitTextArray:
                    if i not in stop_words:
                        print(ps.stem(i))
                        if ps.stem(i) in detailsOfAllData:
                            for j in detailsOfAllData[ps.stem(i)]:
                                for k in splitTextArray:
                                    if j.get("title").find(k) != -1:
                                        j.update(title=re.sub(k, Markup("<mark style = \"background-color: yellow;\">"+k+"</mark>"), j.get('title')))

                                if (result == []):
                                    result.append(j)
                                    print(result)
                                else:
                                    duplicateData = checkDuplicateDocumentAndReturnIt(result, j.get('document_id'))
                                    if (len(duplicateData) > 0):
                                        print("here")
                                        j.update(tf=j.get("tf") + duplicateData[1].get("tf"))
                                        j.update(idf=j.get("idf") + duplicateData[1].get("idf"))
                                        j.update(tf_idf=j.get("tf_idf") + duplicateData[1].get("tf_idf"))
                                    else:
                                        result.append(j)

            except:
                print("exception is here")
                return render_template("error.html")
            sortedResult = sorted(result, key=lambda k: k['tf_idf'], reverse = True )
            return render_template("textResult.html",content = sortedResult)




if __name__ == '__main__':
    app.run()
