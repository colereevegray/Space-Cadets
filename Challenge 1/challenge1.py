import requests
import re
from bs4 import BeautifulSoup
import csv

class Page:
    def __init__(self, url, finalPage=0):
        """
        basic page object: url is required on init in order to request the page, the results of the get request are then passed into a bs4 object
        which allows for easier extraction of the page data.
        """
        
        self.url=url
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.text, "html.parser")
       
        """
        the below lines are used in the case of calling for emails from the main list of people page, finalPage is used to specify how far into the
        people list you want to check.
        """
         
        self.optionalPrefix= "?page="
        self.finalPage=finalPage


class personalPage(Page):
    def __init__(self, url, finalPage=0):
        super().__init__(url, finalPage)

    def getPossibleEmails(self):
        """
        looks for all the emails on a given person's page, also grabs the name if it available (may not be in the same location if calling from
        a specific person's page) in which case the program just continues because you can't stop progress.

        """
        self.divList= self.soup.findAll("a", class_="link-base")
        try:  
            self.name= self.soup.findAll("a", class_="text-endeavour")
        except:
            pass

        #the below two for loops clean the data stored about the emails and names (tags and other elements are stripped from around the text)
        try:
            temp =[]
            for i in self.name:
                temp.append(i.get_text(strip=True))
            self.name= temp
        except:
            pass
        
        self.temp =[]
        for i in self.divList:
            self.temp.append(i.get_text(strip=True))
        self.divList=self.temp
        
        return self.divList, self.name
    
    def doEmailRegEx(self):
        self.getPossibleEmails()
        emailList =[]
        count=0
        #adds details to one large list, (again does not add names in the case of a specific person's page being called)
        for i in self.divList:
            if len(re.findall(r'\S+@\S+',i))>0 and self.finalPage!=0:
                emailList.append([re.findall(r'\S+@\S+',i), self.name[count]])
                count+=1
            elif len(re.findall(r'\S+@\S+',i))>0:
                emailList.append(re.findall(r'\S+@\S+',i))
                count+=1

        self.cleanList =emailList
        return self.cleanList

    #this function handles reading through when the entire staff list is queried (just call doEmailRegEx if you only want one result returned)
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
    
    def banishToCSV(self, filename):
        emailList =self.iterateForEachStaff()

        fields=["email","name"]
        with open(filename, "w") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(fields)
            csv_writer.writerows(emailList)

if __name__ == "__main__":
    page= personalPage('https://www.southampton.ac.uk/people', 435)
    emailList = page.iterateForEachStaff()
    print(emailList)
    page.banishToCSV("massiveList.csv")

    
    
    