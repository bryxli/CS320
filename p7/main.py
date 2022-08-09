# project: p7
# submitter: bli378
# partner: none
# hours: 4

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

class UserPredictor:
    def __init__(self):
        self.model = LogisticRegression(fit_intercept=False)

    def fit(self,users,logs,y):
        users = self.setup(users,logs).merge(y,how="left",on="user_id")
        train,test = train_test_split(users)
        self.model.fit(train[["past_purchase_amt","total_time","const"]],train["y"])

    def predict(self,users,logs):
        users = self.setup(users,logs)
        users["predict"] = self.model.predict(users[["past_purchase_amt","total_time","const"]])
        return users["predict"].to_numpy()

    def setup(self,users,logs):
        users = users.filter(items=["user_id","past_purchase_amt"]).set_index("user_id")
        users["const"] = 1
        users["total_time"] = 0
        for userid in users.index:
            user = logs[logs["user_id"] == userid]
            if len(user) > 0:
                users["total_time"][userid] = sum(user["seconds"])
        return users