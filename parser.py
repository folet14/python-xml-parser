import re
from unicodedata import category
import xml.etree.ElementTree as ET
import jpype
import jaydebeapi

class questionClass:
    def __init__(self, type, quest):
        self.single = None
        self.feedback = None
        self.type = type
        self.quest = quest
        self.answers = []

    def addAnswer(self, answer, fraction):
        self.answers.append((answer, fraction))

    def setFeedback(self, general="", correct="", partial="", incorrect=""):
        self.feedback = [general, correct, partial, incorrect]

    def setSingle(self, value):
        self.single = value

    def getFeedback(self):
        return self.feedback

    def getType(self):
        return self.type

    def getQuestion(self):
        return self.quest

    def getAnswers(self):
        return self.answers

    def getSingle(self):
        return self.single


def XMLparser(filename):
    def removeThingy(text):
        HTMLTag = re.compile('<.*?>')
        insecTag = re.compile('-?&nbsp;?')
        text = re.sub(HTMLTag, '', str(text))
        text = re.sub(insecTag, '', str(text))
        return text


    tree = ET.parse(filename)
    root = tree.getroot()
    if root.tag != "quiz":
        print("wrong xml file, not a quiz")
        exit()

    questionList = []
    for question in root:
        currentType = question.attrib.get("type")
        if currentType == "category":
            pass

        elif currentType == "multichoice":
            for child in question:
                if child.tag == "name":
                    pass
                elif child.tag == "generalfeedback":
                    general = removeThingy(child[0].text)
                elif child.tag == "questiontext":
                    newQuestion = questionClass(currentType, removeThingy(child[0].text))
                elif child.tag == "defaultgrade":
                    pass
                elif child.tag == "penalty":
                    pass
                elif child.tag == "hidden":
                    pass
                elif child.tag == "idnumber":
                    pass
                elif child.tag == "single":
                    single = child.text
                elif child.tag == "shuffleanswers":
                    pass
                elif child.tag == "answernumbering":
                    pass
                elif child.tag == "showstandardinstruction":
                    pass
                elif child.tag == "correctfeedback":
                    correct = removeThingy(child[0].text)
                elif child.tag == "partiallycorrectfeedback":
                    partial = removeThingy(child[0].text)
                elif child.tag == "incorrectfeedback":
                    incorrect = removeThingy(child[0].text)
                elif child.tag == "answer":
                    fraction = child.attrib.get("fraction")
                    newQuestion.addAnswer(
                        removeThingy(child[0].text), fraction)
            newQuestion.setFeedback(general, correct, partial, incorrect)
            newQuestion.setSingle(single)
            questionList.append(newQuestion)

        elif currentType == "truefalse":
            for child in question:
                if child.tag == "name":
                    pass
                elif child.tag == "generalfeedback":
                    general = removeThingy(child[0].text)
                elif child.tag == "questiontext":
                    newQuestion = questionClass(
                        currentType, removeThingy(child[0].text))
                ##elif child.tag == "defaultgrade":
                ##    pass
                ##elif child.tag == "penalty":
                ##    pass
                ##elif child.tag == "hidden":
                ##    pass
                ##elif child.tag == "idnumber":
                ##    pass
                ##elif child.tag == "shuffleanswers":
                ##    pass
                ##elif child.tag == "answernumbering":
                ##    pass
                ##elif child.tag == "showstandardinstruction":
                ##    pass
                elif child.tag == "correctfeedback":
                    correct = removeThingy(child[0].text)
                elif child.tag == "incorrectfeedback":
                    incorrect = removeThingy(child[0].text)
                elif child.tag == "answer":
                    fraction = child.attrib.get("fraction")
                    newQuestion.addAnswer(
                        removeThingy(child[0].text), fraction)
            newQuestion.setFeedback(general = general,correct =  correct, incorrect = incorrect)
            questionList.append(newQuestion)

    return questionList

def Upload(questionList):
    JHOME = jpype.getDefaultJVMPath()
    
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=['jar/ojdbc6.jar'])
    con = jaydebeapi.connect('oracle.jdbc.driver.OracleDriver',
                            'jdbc:oracle:thin:legoffad/47671b85b1@im2ag-oracle.e.ujf-grenoble.fr:1521:im2ag')
    cur = con.cursor()
    nbQst = 0
    for question in questionList:
        nbQst+=1
        enonce = question.getQuestion()
        reponses = question.getAnswers()
        general = question.getFeedback()[0]
        nbRep=0
        for i in reponses:
            nbRep+=1

        if(nbRep == 2):
            #Question vrai/faux
            err = 0
            if(reponses[0][0] == reponses[1][0]):
                err = 1
                print("probleme de reponses dupliquees pour la question "+enonce)
            if err == 0:
                stmt = "INSERT INTO Questions VALUES(NULL, 1, 'None','"+enonce+"','"+general+"')"
                try:
                    cur.execute(stmt)
                    print("inserted :"+stmt)
                except jaydebeapi.DatabaseError as e:
                    print("Couldn't exec request "+stmt)
                    err = 1
                if(err == 0):
                    stmt ="SELECT ID FROM Questions WHERE question='"+enonce+"'"
                    cur.execute(stmt)

                    for i in cur.fetchall():
                        id = i[0]

                    for rep in reponses:
                        if int(float(rep[1])) == 100:
                            stmt = "INSERT INTO Reponses VALUES("+str(id)+", '"+rep[0]+"', "+str(int(float(rep[1])))+",'"+question.getFeedback()[1]+"')"
                        elif int(float(rep[1])) == 0:
                            stmt = "INSERT INTO Reponses VALUES("+str(id)+", '"+rep[0]+"', "+str(int(float(rep[1])))+",'"+question.getFeedback()[3]+"')"
                        else:
                            stmt = "INSERT INTO Reponses VALUES("+str(id)+", '"+rep[0]+"', "+str(int(float(rep[1])))+",'"+question.getFeedback()[2]+"')"

                        try:
                            cur.execute(stmt)
                            print("inserted :"+stmt)
                        except jaydebeapi.DatabaseError as e:
                            print("Couldn't exec request "+stmt)
        else:
            #Question QCM avec 1 ou plusieurs reponses juste
            nbRepJuste = 0
            err = 0
            previous = []
            for rep in reponses:

                for p in previous :
                    if(p[0] == rep[0]):
                        print("probleme de reponses dupliquees pour la question "+enonce)
                        err = 1
                previous.append(rep)

                if(0<int(float(rep[1]))<100):
                    nbRepJuste = 2

            if(err ==  0):
                stmt = "INSERT INTO Questions VALUES(NULL, "+str(nbRepJuste)+", 'None','"+enonce+"','"+general+"')"
                try:
                    cur.execute(stmt)
                    print("inserted :"+stmt)

                except Exception as ex:
                    print("Couldn't exec request "+stmt)
                    err = 1

                if err == 0:

                    stmt = "SELECT ID FROM Questions WHERE question='"+enonce+"'"
                    cur.execute(stmt)

                    for i in cur.fetchall():
                        id = i[0]

                    for rep in reponses:
                        if int(float(rep[1])) == 100:
                            stmt = "INSERT INTO Reponses VALUES("+str(id)+", '"+rep[0]+"', "+str(int(float(rep[1])))+",'"+question.getFeedback()[1]+"')"
                        elif int(float(rep[1])) == 0 :
                            stmt = "INSERT INTO Reponses VALUES("+str(id)+", '"+rep[0]+"', "+str(int(float(rep[1])))+",'"+question.getFeedback()[3]+"')"
                        else:
                            stmt = "INSERT INTO Reponses VALUES("+str(id)+", '"+rep[0]+"', "+str(int(float(rep[1])))+",'"+question.getFeedback()[2]+"')"
                        try:
                            cur.execute(stmt)
                            print("inserted :"+stmt)
                        except jaydebeapi.DatabaseError as e:
                            print("Couldn't exec request "+stmt)
