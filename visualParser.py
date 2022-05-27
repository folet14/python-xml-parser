import copy
import parser as p
import tkinter as tk
from tkinter import filedialog


class visualParser(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.questionList = []
        self.curr = 0
        self.nbQuest = 0
        for F in (SelectionPage, CorrectionPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("SelectionPage")

    def setQuestionList(self, list):
        self.questionList = copy.deepcopy(list)

    def popQuestionNb(self, nb):
        if self.nbQuest > nb:
            return self.questionList.pop(nb)

    def addQuestion(self, question):
        self.questionList.append(question)

    def changeNbQuest(self, nb):
        self.nbQuest = nb

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class SelectionPage(tk.Frame):

    def __init__(self, questionList, parent, controller):

        def UploadAction(questionList, event=None):
            filename = filedialog.askopenfilename(filetypes=(("XML Files", "*.xml"),),title = "XML file selection", multiple = False)
            print('Selected:', filename)
            controller.setQuestionList(p.XMLparser(filename))
            controller.changeNbQuest(len(questionList))
            controller.show_frame("CorrectionPage")

        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is the start page")
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Select XML", command=lambda: UploadAction(questionList))
        button1.pack()

class CorrectionPage(tk.Frame):

    def __init__(self, questionList, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is CorrectionPage")
        label.pack(side="top", fill="x", pady=10)

        label = tk.Label(self, textvariable=question)

        button = tk.Button(self, text="Reset", command=lambda: controller.show_frame("SelectionPage"))
        button.pack()

if __name__ == "__main__":
    app = visualParser()
    app.mainloop()