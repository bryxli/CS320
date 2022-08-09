import json
from zipfile import ZipFile
from io import TextIOWrapper
import csv

race_lookup = {
    "1": "American Indian or Alaska Native",
    "2": "Asian",
    "21": "Asian Indian",
    "22": "Chinese",
    "23": "Filipino",
    "24": "Japanese",
    "25": "Korean",
    "26": "Vietnamese",
    "27": "Other Asian",
    "3": "Black or African American",
    "4": "Native Hawaiian or Other Pacific Islander",
    "41": "Native Hawaiian",
    "42": "Guamanian or Chamorro",
    "43": "Samoan",
    "44": "Other Pacific Islander",
    "5": "White",
}

class Applicant:
    def __init__(self, age, race):
        self.age = age
        self.race = set()
        for r in race:
            if r in race_lookup:
                self.race.add(race_lookup[r])
            
    def __repr__(self):
        output = "Applicant('"+self.age+"', ["
        check = False
        for r in self.race:
            output+="'"+r+"', '"
            check = True
        if check:
            output = output[:-3]
        output += "])"
        return output
    
    def lower_age(self):
        if "-" in self.age:
            return int(self.age.split("-")[0])
        elif "<" in self.age:
            return int(self.age[1:])
        elif ">" in self.age:
            return int(self.age[1:])
        
    def __lt__(self, other):
        if int(Applicant.lower_age(self)) < int(Applicant.lower_age(other)):
            return True
        return False
    
class Loan:
    def __init__(self, values):
        self.loan_amount = self.convert_to_float(values["loan_amount"])
        self.property_value = self.convert_to_float(values["property_value"])
        self.interest_rate = self.convert_to_float(values["interest_rate"])
        self.applicants = []
        number = self.applicant_race_number(5, values)
        races = []
        for i in range(1,number+1):
            races.append(values["applicant_race-" + str(i)])    
        self.applicants.append(Applicant(values["applicant_age"],races))
        if values["co-applicant_age"] != "9999":
            number = self.coapplicant_race_number(5, values)
            races = []
            for i in range(1,number+1):
                races.append(values["co-applicant_race-" + str(i)])
            self.applicants.append(Applicant(values["co-applicant_age"],races)
                                 )
            
    def __str__(self):
        return "<Loan: " + str(self.interest_rate) + "% on $" + str(self.property_value) + " with " + str(len(self.applicants)) + " applicant(s)>"
        
    def __repr__(self):
        return str(self)
    
    def convert_to_float(self, string):
        missing = ["NA","Exempt"]
        if string in missing:
            return -1
        else:
            return float(string)
        
    def applicant_race_number(self, number_of_races, values):
        if number_of_races > 1 and values["applicant_race-" + str(number_of_races)] == "":
            return self.applicant_race_number(number_of_races - 1, values)
        else:
            return number_of_races

    def coapplicant_race_number(self, number_of_races, values):
        if number_of_races > 1 and values["co-applicant_race-" + str(number_of_races)] == "":
            return self.coapplicant_race_number(number_of_races - 1, values)
        else:
            return number_of_races
        
    def yearly_amounts(self, yearly_payment):
        amt = self.loan_amount
        ir = self.interest_rate/100
        assert amt > 0 and ir > 0
        while amt > 0:
            yield(amt)
            amt = ir * amt + amt - yearly_payment
            
class Bank:
    def __init__(self, name):
        with open("banks.json") as f:
            data = json.load(f)
        for bank in data:
            if name in str(bank):
                self.lei = str(bank)[9:29]
                break
        self.list = []
        with ZipFile("wi.zip") as zf:
            with zf.open("wi.csv") as f:
                tio = TextIOWrapper(f)
                reader = csv.DictReader(tio)
                for row in reader:
                    if row["lei"] == self.lei:
                        self.list.append(Loan(row))
                        
    def __len__(self):
        return len(self.list)
    
    def __getitem__(self, index):
        return self.list[index]