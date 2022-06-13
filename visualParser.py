import GreenGoparser as p
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


##---------------------------unique window------------------------------------
class visualParser(tk.Tk):
  def __init__(self, *args, **kwargs):
    tk.Tk.__init__(self, *args, **kwargs)
    container = tk.Frame(self)
    self.title('Parser')
    container.pack(side="top", fill="both", expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    ##--------generating two frames------------
    self.frames = {}
    for F in (uploadPage, questionPage):  ##uploadPage for the xml import, question page to visualise and edit questions
      page_name = F.__name__
      frame = F(parent=container, controller=self)
      self.frames[page_name] = frame
      frame.grid(row=0, column=0, sticky="nsew")
    self.show_frame("uploadPage")

  ##-------------unique window----------
  def show_frame(self, page_name):
    frame = self.frames[page_name]
    frame.tkraise()

  ##-------when xml is imported we initialise correctly the question page----------
  def startQuestionPage(self, questionList):
    questionPage = self.frames["questionPage"]
    questionPage.setQuestionList(questionList)
    questionPage.startEdition()
    questionPage.tkraise()


##-----------------------------XML Frame definition------------------------------------
class uploadPage(tk.Frame):
  def __init__(self, parent, controller):
    def UploadAction(questionList, event=None):
      filename = filedialog.askopenfilename(filetypes=(("XML Files", "*.xml"),), title="XML file selection",
                                            multiple=False)
      print('Selected:', filename)
      questionList = p.XMLparser(filename)
      if questionList != []:
        controller.startQuestionPage(questionList)

    tk.Frame.__init__(self, parent)
    self.controller = controller
    label = tk.Label(self, text="This is the upload page")
    label.pack(side="top", fill="x", pady=10)
    self.questionList = []
    button1 = tk.Button(self, text="Select XML", command=lambda: UploadAction(self.questionList))
    button1.pack()


##---------------------------------Question edition frame-------------------------------------
class questionPage(tk.Frame):
  isStarted = False

  ##-------to remove every widget from the page----
  def clear_question(self):
    widgetList = self.winfo_children()
    for widget in widgetList:
      widget.destroy()

  ##---------as if nothing ever happend--------------
  def reset(self):
    self.index = 0
    self.clear_question()
    self.controller.show_frame("uploadPage")

  ##---------just basic useful variables--------------
  def __init__(self, parent, controller):
    tk.Frame.__init__(self, parent)
    self.controller = controller
    self.index = 0
    self.typeVariable = tk.StringVar()

  ##----------show next question if any---------
  def next(self):
    if self.index < self.nbQuest - 1:
      self.index += 1
      self.clear_question()
      self.startEdition()
    else:
      tk.messagebox.showinfo(title = None, message = "no more questions")
      print("no more question")

  ##----------show previous question if any---------
  def previous(self):
    if self.index > 0:
      self.index -= 1
      self.clear_question()
      self.startEdition()
    else:
      tk.messagebox.showinfo(title = None, message ="no previous question")
      print("already first question")

  ##----------to get QuestionList from xml---------
  def setQuestionList(self, questionList):
    self.questionList = questionList
    self.nbQuest = len(self.questionList)

  ##----------restrain entry box value to float between -100 100---------
  def isInt(self, value_if_allowed):
    try:
      value = float(value_if_allowed)
      return value >= -100 and value <= 100
    except ValueError:
      return value_if_allowed == ""

  ##----------store inputed data---------
  def save(self):
    type = self.typeVariable.get()
    if type == "Multichoice" or type == "SingleChoice":
      newQuestion = p.questionClass("multichoice", self.questEntry.get())
      if type == "Multichoice":
        newQuestion.setSingle("false")
      else: 
        newQuestion.setSingle("true")
    else:
      newQuestion = p.questionClass("truefalse", self.questEntry.get())

    if self.questEntry.get()=="":
      tk.messagebox.showwarning(title="Warning", message="make sure all the informations are filled")
      return
    fbackList = []
    for fback in self.feedbackTextList:
      fbackList.append(fback.get())
    general = fbackList[0]
    correct = fbackList[1]
    if type != "truefalse":
      if len(fbackList) == 4:
        partial = fbackList[2]
        incorrect = fbackList[3]
        newQuestion.setFeedback(general=general, correct=correct, partial=partial, incorrect=incorrect)
      else:
        incorrect = fbackList[2]
        newQuestion.setFeedback(general=general, correct=correct, incorrect=incorrect)
    elif type == "truefalse":
      incorrect = fbackList[2]
      newQuestion.setFeedback(general=general, correct=correct, incorrect=incorrect)
    
    for i in fbackList:
      if i == "":
        tk.messagebox.showwarning(title="Warning", message="make sure all the informations are filled")
        return
    for quest in self.answerTextList:
      if quest[0].get()=="" or quest[1].get()=="":
        tk.messagebox.showwarning(title="Warning", message="make sure all the informations are filled")
        return
      newQuestion.addAnswer(quest[0].get(), quest[1].get())
    self.questionList[self.index] = newQuestion
    self.clear_question()
    self.startEdition()

  ##----------delete the row j of answer---------
  def deleteRow(self, j):
    if len(self.answerTextList) > 2:
      for w in self.answerTextList[j]:
        w.destroy()
      self.answerTextList.pop(j)
    else:
      print("at least 2 answers")

  ##----------add a row of answer (save is necessary)---------
  def addRow(self):
    onlyInt = (self.register(self.isInt), '%P')
    answerText = tk.Entry(self)
    answerValue = tk.Entry(self, validate="key", validatecommand=onlyInt)
    answerText.insert('end', "")
    answerValue.insert('end', "")
    self.answerTextList.append((answerText, answerValue))
    self.save()

  ##---------------------------------------------TEST----------------------------------
  def deleteQuestion(self):
    if self.nbQuest > 1:
      self.nbQuest -= 1
      self.questionList.pop(self.index)
      while self.index >= self.nbQuest:
        self.index -= 1
      self.clear_question()
      self.startEdition()

  def addQuestion(self):
    self.nbQuest += 1
    defaultQuestion = p.questionClass("truefalse", "")
    defaultQuestion.addAnswer("true", "100")
    defaultQuestion.addAnswer("false", "0")
    defaultQuestion.setFeedback()
    self.questionList.insert(self.index, defaultQuestion)
    self.clear_question()
    self.startEdition()


  ##--------------------final function to import question-------------
  def checking(self):
    ##TODO
    

    return self.questionList

  def importQuest(self):
    finalList = self.checking()
    p.Upload(finalList)

  ##-------initialise page at the current question index-------------------
  def startEdition(self):
    ##headers buttons
    button = tk.Button(self, text="Reset", command=self.reset)
    button.grid(row=0, column=1)
    previousButton = tk.Button(self, text="previous", command=self.previous)
    previousButton.grid(row=0, column=0)
    nextButton = tk.Button(self, text="next", command=self.next)
    nextButton.grid(row=0, column=2)
    addQuestButton = tk.Button(self, text="add question", command=self.addQuestion)
    addQuestButton.grid(row=0, column=3)
    removeQuestButton = tk.Button(self, text="delete question", command=self.deleteQuestion)
    removeQuestButton.grid(row=0, column=4)

    ##---question----
    if self.nbQuest > 0:

      i = self.index
      currentQuestion = self.questionList[i]

      ##typeEntry = tk.Entry(self)
      ##typeEntry.insert('end', self.questionList[i].getType())

      ##here is type combobox
      type = currentQuestion.getType()
      self.typeCombo = ttk.Combobox(self, values=["Multichoice", "SingleChoice", "True/False"], state="readonly",
                                    textvariable=self.typeVariable)
      if type != "":
        if type == "multichoice":
          if currentQuestion.getSingle() == "true":
            self.typeCombo.current(1)
          elif currentQuestion.getSingle() == "false":
            self.typeCombo.current(0)
        elif type == "truefalse":
          self.typeCombo.current(2)
      typeText = tk.Label(self, text="type: ")

      ##question text
      self.questEntry = tk.Entry(self, width = 70)
      self.questEntry.insert('end', currentQuestion.getQuestion())

      questText = tk.Label(self, text="question: ")

      typeText.grid(row=1, column=0)
      ##typeEntry.pack(side="top", fill="x")
      self.typeCombo.grid(row=1, column=1)
      questText.grid(row=2, column=0)
      self.questEntry.grid(row=2, column=1)

      ##answers
      answText = tk.Label(self, text="Answers: ")
      answText.grid(row=3, column=0)
      self.answerTextList = []

      onlyInt = (self.register(self.isInt), '%P')
      if type != "truefalse":
        answers = currentQuestion.getAnswers()
        for j in range(len(answers)):
          answerText = tk.Entry(self, width = 70)
          answerValue = tk.Entry(self,validate="key", validatecommand=onlyInt)
          answerText.insert('end', answers[j][0])
          answerValue.insert('end', answers[j][1])

          answerText.grid(row=4 + j, column=0)
          answerValue.grid(row=4 + j, column=1)
          deleteAnswer = tk.Button(self, text="delete", command=lambda t=j: self.deleteRow(t))
          deleteAnswer.grid(row=4 + j, column=2)
          self.answerTextList.append((answerText, answerValue, deleteAnswer))
      else:
        answers = [("true", 100), ("false", 0)]
        for j in range(2):
          answerText = tk.Entry(self)
          answerValue = tk.Entry(self)
          answerText.insert('end', answers[j][0])
          answerValue.insert('end', answers[j][1])
          answerText.config(state='disabled')
          answerValue.config(state='disabled')
          answerText.grid(row=4 + j, column=0)
          answerValue.grid(row=4 + j, column=1)
          self.answerTextList.append((answerText, answerValue))

      ##feedbacks
      feedbackList = currentQuestion.getFeedback()
      self.feedbackTextList = []
      general = tk.Entry(self, width =50)
      general.insert('end', feedbackList[0])
      startfeedBack = 4 + len(answers)
      feedbackLabel = tk.Label(self, text="Feedback:")
      feedbackLabel.grid(row=startfeedBack, column=0)
      general.grid(row=startfeedBack + 1, column=0)
      self.feedbackTextList.append(general)
      if type != "":
        if type == "multichoice":
          correct = tk.Entry(self, width =50)
          partial = tk.Entry(self,width =50)
          incorrect = tk.Entry(self,width =50)
          correct.insert('end', feedbackList[1])
          partial.insert('end', feedbackList[2])
          incorrect.insert('end', feedbackList[3])
          correct.grid(row=startfeedBack + 2, column=0)
          partial.grid(row=startfeedBack + 3, column=0)
          incorrect.grid(row=startfeedBack + 4, column=0)
          next = startfeedBack + 5
          self.feedbackTextList.append(correct)
          self.feedbackTextList.append(partial)
          self.feedbackTextList.append(incorrect)

        elif type == "truefalse":
          correct = tk.Entry(self)
          incorrect = tk.Entry(self)
          correct.insert('end', feedbackList[1])
          incorrect.insert('end', feedbackList[3])
          correct.grid(row=startfeedBack + 2)
          incorrect.grid(row=startfeedBack + 3)
          next = startfeedBack + 4
          self.feedbackTextList.append(correct)
          self.feedbackTextList.append(incorrect)

      ##bottom buttons
      saveButton = tk.Button(self, text="save", command=self.save)
      saveButton.grid(row=25)
      addAnsButton = tk.Button(self, text="add answer", command=self.addRow)
      addAnsButton.grid(row=25, column=1)
      finalButton = tk.Button(self, text="import question", command = self.importQuest)
      finalButton.grid(row=25, column=2)
if __name__ == "__main__":
  app = visualParser()
  app.mainloop()
