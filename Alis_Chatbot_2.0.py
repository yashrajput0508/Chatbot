import sys
import pandas as pd
from keras.preprocessing import text
from nltk import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import wikipedia
from details import *
from template import *
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QMessageBox,QAction
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QDate
import Database as db
import sqlite3

class gui(QMainWindow):
    def __init__(self):
        super().__init__()
        # adding the window title and window icon on frame
        self.setWindowTitle("Chatbot")
        self.setWindowIcon(QIcon(r'chatbot.png'))

        # accessing the frame model
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)

        # it is the send button which send your message
        self.ui.pushButton.clicked.connect(self.maintain)

        # adding the action button if click on enter button on keyboard it send the message
        action = QAction(self)
        action.setShortcut("Return")
        self.addAction(action)
        action.triggered.connect(self.maintain)

        # adding the font size on frame where the messages are shown
        font1 = QFont()
        font1.setPointSize(12)
        self.ui.plainTextEdit.setFont(font1)

        # focus on the message box where you write the message
        self.ui.lineEdit.setFocus()

        # it change the your name which is used by bot
        self.ui.actionChange_details.triggered.connect(self.change_owner_name)

        # it takes the owner_name
        self.owner_name=self.owner_database()[0]
        self.ui.plainTextEdit.setPlainText("Alis: Hello {}, My name is Alis. How can I help you".format(self.owner_name))

        # accessing the data class where the chatbot model is trained
        self.working=working()

        # creating the database where we store the messages
        db.database()

        # if reply==False:
        #     self.ui.plainTextEdit.appendPlainText("Alis: Sir if you want to save your details Go to File->Change Details")

        self.show()

    def maintain(self):
        # it handles the message in frame and send the response to the user
        user_response = self.ui.lineEdit.text()
        user_response = user_response.lower()

        # it takes the response from the model
        response = self.working.response(user_response)

        # show the text into the message box
        self.ui.plainTextEdit.appendPlainText("{}: ".format(self.name)+user_response)

        # if user write exit than it exit from app else continue conversation
        if (user_response != 'exit'):

            # input and response save to database
            if response != "Sir Please Give more information" or response != "Please Connect to internet":
                try:
                    db.updatedatabase(user_response, str(response))
                except Exception as e:
                    pass
            # show the response into the frame
            self.ui.plainTextEdit.appendPlainText("Alis: " + response.replace("sir", self.name))

        else:
            self.flag = False
            self.ui.plainTextEdit.appendPlainText("Alis: Thanks for conversations,Bye...")
            self.destroy()

        # it clear the text where we write message
        self.ui.lineEdit.clear()

    def change_owner_name(self):

        # it changes the name from database
        conn=sqlite3.connect("database.db")
        c=conn.cursor()

        # accessing data class which changes the owerner details
        self.data = data()
        name=self.owner_database()[0]
        date=self.owner_database()[1]
        self.data.ui.lineEdit.setText(name)
        date=date.split("-")
        self.data.ui.dateEdit.setDate(QDate(int(date[-1]),int(date[-2]),int(date[-3])))
        self.data.exec()

        # update the name and data of birth
        try:
            c.execute("UPDATE info set name='{}' where id=1".format(self.data.name))
            c.execute("UPDATE info set date='{}' where id=1".format(self.data.date))
            conn.commit()
            self.name=self.data.name
        except Exception as e:
            print(e)
        c.close()

    def owner_database(self):
        # it create the database of owner name and data of birth
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # if database exsist then fetch name and if not then create a database of name and DOB
        try:
            c.execute("SELECT * FROM info")
            self.name,self.date = c.fetchall()[0][1:]
            c.close()
            return [self.name,self.date]
        except sqlite3.OperationalError:
            c.execute("CREATE TABLE info(id INTEGER PRIMARY KEY AUTOINCREMENT,name,date)")
            c.execute("INSERT INTO info (name,date) VALUES('Yash','05-08-2001')")
            self.name = "Yash"
            self.date ='05-08-2001'
            conn.commit()
            c.close()
            return [self.name,self.date]

class data(QDialog):
    def __init__(self):
        super().__init__()
        # it is the frame which takes the name and DOB of owner
        self.ui=Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.enquiry)
        self.show()

    def enquiry(self):
        # it takes the data from owner and send to the database
        self.name=self.ui.lineEdit.text()
        self.date=self.ui.dateEdit.text()
        if self.name=="":
            QMessageBox.warning(self,"Name Error","Please enter you name sir")
        else:
            QMessageBox.information(self,"Information saved","Thanks to share your information")
            Gui.ui.plainTextEdit.appendPlainText("Alis: Thank to share your details {}".format(self.name))


class working:
    def __init__(self):
        # it takes the data from json files
        self.data = pd.read_json("intents.json")
        self.lemmer = WordNetLemmatizer()
        self.LemNormalize = text.text_to_word_sequence

        # the data is divided into patterns, tags and responses format
        self.patterns = []
        self.tags = []
        self.responses = []

        for i in self.data['intents']:
            self.patterns.extend([" ".join(text.text_to_word_sequence(j)) for j in i['patterns']])
            self.tags.extend(i['responses'])

    def databases(self):
        # it takes the data from database which save your every message and make chatbot more knowledgeable
        if db.database() == True:
            inputs, rest = db.get_update()
            for i, j in zip(inputs, rest):
                self.patterns.append(i)
                self.tags.append(j)

    def execution(self,sentence):
        try:
            return wikipedia.summary(sentence, 1)
        except wikipedia.PageError:
            return "Sir Please Give more information"
        except ConnectionError:
            return "Please Connect to internet"
        except Exception as e:
            return "Please Connect to internet"

    def response(self,sentence):
        # here is the chatbot model where it is trained
        robo_response = ''
        self.patterns.append(" ".join(text.text_to_word_sequence(sentence)))
        TfidfVec = TfidfVectorizer(stop_words='english')
        tfidf = TfidfVec.fit_transform(self.patterns)
        self.patterns.pop(-1)
        vals = cosine_similarity(tfidf[-1], tfidf)
        idx = np.argmax(vals)
        if (idx >= len(vals[0]) - 1):
            return self.execution(sentence)
        else:
            ans = self.tags[idx]
            robo_response = robo_response + ans
            return robo_response

    """print("I am alis a chatbot how can i help you?")
    while True:
        result = input("You : ")
        ans1 = response(result)
        print("Alis: ", ans1)"""


if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setWindowIcon(QIcon(r'chatbot.png'))
    Gui=gui()
    Gui.show()
    app.exec()