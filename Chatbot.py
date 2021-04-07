import io
import json
import random
import string
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import warnings
warnings.filterwarnings('ignore')
from details import *
from template import *
import nltk
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QMessageBox,QAction
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QTime, QDate
from nltk.stem import WordNetLemmatizer
class gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chatbot")
        self.setWindowIcon(QIcon(r'roboimg.png'))
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.operator=project()
        reply=self.operator.database()
        self.ui.plainTextEdit.setPlainText("Alis: Hello {}, My name is Alis. How can I help you".format(self.operator.name))
        if reply==False:
            self.ui.plainTextEdit.appendPlainText("Alis: Sir if you want to save your details Go to File->Change Details")
        self.ui.pushButton.clicked.connect(self.maintain)
        font1=QFont()
        font1.setPointSize(12)
        action=QAction(self)
        action.setShortcut("Return")
        self.addAction(action)
        action.triggered.connect(self.maintain)
        self.ui.plainTextEdit.setFont(font1)
        self.ui.lineEdit.setFocus()
        self.ui.actionChange_details.triggered.connect(self.change)
        self.show()
    def maintain(self):
        user_response = self.ui.lineEdit.text()
        self.ui.plainTextEdit.appendPlainText("{}: ".format(self.operator.name)+user_response)
        user_response = user_response.lower()
        response=self.operator.greeting(user_response)
        if (user_response != 'exit'):
            self.ui.plainTextEdit.appendPlainText("Alis: "+response.replace("tg",self.operator.name))
        else:
            self.flag = False
            self.ui.plainTextEdit.appendPlainText("Alis: Thanks for conversations,Bye...")
            self.destroy()
        self.ui.lineEdit.clear()
    def change(self):
        conn=sqlite3.connect("database.db")
        c=conn.cursor()
        a=data()
        c.execute("SELECT * from data")
        datas=c.fetchall()[0]
        a.ui.lineEdit.setText(datas[1])
        date=datas[2].split("-")
        a.ui.dateEdit.setDate(QDate(int(date[-1]),int(date[-2]),int(date[-3])))
        a.exec()
        try:
            c.execute("UPDATE data set name='{}' where id=1".format(a.name))
            c.execute("UPDATE data set date='{}' where id=1".format(a.date))
            conn.commit()
            self.operator.name=a.name
        except:
            pass
        c.close()
class data(QDialog):
    def __init__(self):
        super().__init__()
        self.ui=Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.enquiry)
        self.show()
    def enquiry(self):
        self.name=self.ui.lineEdit.text()
        self.date=self.ui.dateEdit.text()
        if self.name==" ":
            QMessageBox.warning(self,"Name Error","Please enter you name sir")
        else:
            QMessageBox.information(self,"Information saved","Thanks to share your information")
            Gui.ui.plainTextEdit.appendPlainText("Alis: Thank to share your details {}".format(self.name))
            self.close()
    def close(self):
        if self.name=="":
            self.ui.lineEdit.setText("Sir")
            self.name="Sir"

class project:
    def __init__(self):
        #nltk.download('popular')
        # nltk.download('punkt')
        # nltk.download('wordnet')
        # Reading in the corpus
        #self.TfidfVec1 = TfidfVectorizer(tokenizer=self.LemNormalize,stop_words='english')
        #with open('chatbot.txt', 'r', encoding='utf8', errors='ignore') as fin:
            #raw = fin.read().lower()
            #self.sent_tokens = nltk.sent_tokenize(raw)  # converts to list of sentences
            #word_tokens = nltk.word_tokenize(raw)  # converts to list of words
        self.remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
        self.lemmer = WordNetLemmatizer()
        self.dataimport()
        self.TfidfVec = TfidfVectorizer(tokenizer=self.LemNormalize)
        self.TfidfVec.fit_transform(self.patterns)
    def LemTokens(self,tokens):
        return [self.lemmer.lemmatize(token) for token in tokens]
    def LemNormalize(self,text):
        return self.LemTokens(nltk.word_tokenize(text.lower().translate(self.remove_punct_dict)))
    def dataimport(self):
        file = open(r"jss.json", "r", errors="ignore").read()
        data = json.loads(file)
        self.patterns = []
        self.response = []
        for i in data['intents']:
            self.patterns.extend(i['patterns'])
            self.response.extend(i['responses'])
    def database(self):
        conn=sqlite3.connect("database.db")
        c=conn.cursor()
        try:
            c.execute("SELECT * FROM data")
            self.name=c.fetchall()[0][1]
            c.close()
            return True
        except sqlite3.OperationalError:
            c.execute("CREATE TABLE data(id INTEGER PRIMARY KEY AUTOINCREMENT,name,date)")
            c.execute("INSERT INTO data (name,date) VALUES('Sir','01-01-2001')")
            self.name="Sir"
            conn.commit()
            c.close()
            return False
    def greeting(self,sentence):
        self.patterns.append(sentence)
        """If user's input is a greeting, return a greeting response"""
        tfidf = self.TfidfVec.fit_transform(self.patterns)
        vals = cosine_similarity(tfidf[-1], tfidf)
        idx = vals.argsort()[0][-2]
        flat = vals.flatten()
        flat.sort()
        self.patterns.pop(-1)
        req_tfidf = flat[-2]
        if (req_tfidf == 0):
            robo_response =  "I am sorry! I don't understand you"
            return robo_response
        else:
            robo_response = self.response[idx]
            return robo_response
if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setWindowIcon(QIcon(r'roboimg.png'))
    Gui=gui()
    Gui.show()
    app.exec()