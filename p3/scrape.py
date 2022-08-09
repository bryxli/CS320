# project: p3
# submitter: bli378
# partner: none
# hours: 10
import pandas as pd
import time
import requests

class Parent:
    def twice(self):
        self.message()
        self.message()
        
    def message(self):
        print("parent says hi")
        
class Child(Parent):
    def message(self):
        print("child says hi")
        
class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        self.names = []
        self.visited = set()
        self.order = []
        self.dfs_visit(node)

    def dfs_visit(self, node):
        if node in self.visited:
            return
        self.visited.add(node)
        self.order.append(node)
        children = self.go(node)
        
        orderedchildren = []
        for i in range(len(children)):
            if ".txt" in children[i]:
                with open("file_nodes/"+children[i]) as f:
                    name = f.readlines()[0][:-1]
                    orderedchildren.append([name,i])
            else:
                orderedchildren.append([children[i],i])
        orderedchilden = sorted(orderedchildren,key=lambda x: x[0])
        
        for i in orderedchildren:
            self.dfs_visit(children[i[1]])
    
    def bfs_search(self, node):
        self.names = []
        self.queue = [node]  
        self.visited = set() 
        self.order = []
        
        while len(self.queue) > 0:
            check_node = self.queue.pop(0)
            if check_node in self.visited:
                continue
            self.order.append(check_node)
            self.visited.add(check_node)
            children = self.go(check_node)
            
            orderedchildren = []
            for i in range(len(children)):
                if ".txt" in children[i]:
                    with open("file_nodes/"+children[i]) as f:
                        name = f.readlines()[0][:-1]
                        orderedchildren.append([name,i]) #name of node, position i (0 or 1)
                else:
                    orderedchildren.append([children[i],i]) #value in child i, position i (0 or 1)
            orderedchilden = sorted(orderedchildren,key=lambda x: x[0]) #sort by value 0
            
            for i in orderedchildren:
                if not i[0] in self.visited:
                    self.queue.append(children[i[1]])
                    
class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__()
        self.df = df

    def go(self, node):
        children = []
        for node, has_edge in self.df.loc[node].items():
            if has_edge:
                children.append(node)
        return children
    
class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()
        self.directory = "file_nodes/"
        self.names = []
        
    def go(self, file):
        file = self.directory+file
        with open(file) as f:
            lines = f.readlines()
            name = lines[0]
            children = lines[1]
        if not name in self.names:
            self.names.append(name)
        children = children.split(",")
        children[-1] = children[-1][:-1]
        return children
    
    
    def message(self):
        output = ""
        for i in self.names:
            output += i[0:-1]
        return output
    
class WebSearcher(GraphSearcher):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.tables = []
        
    def go(self, url):
        output = []
        self.driver.get(url)
        links = self.driver.find_elements(by="tag name", value="a")
        for link in links:
            url = link.get_attribute("href")
            output.append(url)
            self.tables.append(pd.read_html(url))
        return output
    
    def table(self):
        output = pd.DataFrame()
        for table in self.tables:
            for df in table:
                output = pd.concat([output,df],ignore_index=True)
        return output
    
def reveal_secrets(driver, url, travellog):
    clues = travellog["clue"].tolist()
    password = ""
    for clue in clues:
        password += str(clue)
    driver.get(url)
    driver.find_element(value="password").send_keys(password)
    driver.find_element(value="attempt-button").click()
    time.sleep(0.5)
    driver.find_element(value="securityBtn").click()
    time.sleep(1)
    
    # https://thomaslevine.com/computing/downloading-binary-files/
    r = requests.get(driver.current_url)
    with open("Current_Location.jpg","wb") as f:
        f.write(r.content)
        
    return driver.find_element(value="location").text
    
    
