import requests
import re
from bs4 import BeautifulSoup
import csv

class Page:
    def __init__(self, url, finalPage=0):
        self.url=url
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.text, "html.parser")
        self.optionalPrefix= "?page="
        self.finalPage=finalPage


class personalPage(Page):
    def __init__(self, url, finalPage=0):
        super().__init__(url, finalPage)

    def getPossibleEmails(self):
        self.divList= self.soup.findAll("a", class_="link-base")
        self.name= self.soup.findAll("a", class_="text-endeavour")
        temp =[]
        for i in self.name:
            temp.append(i.get_text(strip=True))
        self.name= temp
        self.temp =[]
        for i in self.divList:
            self.temp.append(i.get_text(strip=True))
        self.divList=self.temp
        
        return self.divList
    
    def doEmailRegEx(self):
        self.getPossibleEmails()
        emailList =[]
        count=0
        for i in self.divList:
            if len(re.findall(r'\S+@\S+',i))>0:
                emailList.append([re.findall(r'\S+@\S+',i), self.name[count]])
                count+=1

            
        self.cleanList =emailList
        return self.cleanList

    def iterateForEachStaff(self):
        k=0
        self.largeList=[]
        while k <= self.finalPage:
            self.page= requests.get(self.url+self.optionalPrefix+str(k))
            self.soup= BeautifulSoup(self.page.text, "html.parser")
            self.largeList.append(self.doEmailRegEx())
            k+=1

        self.cleanedLargeList =[]
        for i in self.largeList:
            for j in range(0, len(i)):
                self.cleanedLargeList.append(i[j])
        return self.cleanedLargeList
    
    
if __name__ == "__main__":
    page= personalPage('https://www.southampton.ac.uk/people', 435)
    emailList = page.iterateForEachStaff()
    print(emailList)
    fields=["email","name"]
    with open("massiveList.csv", "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(fields)
        csv_writer.writerows(emailList)