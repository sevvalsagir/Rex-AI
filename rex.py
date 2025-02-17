from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

iris = load_iris()
x_train, x_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.3)

model = DecisionTreeClassifier()
model.fit(x_train, y_train)
accuracy = model.score(x_test, y_test)
print(f"Decision Tree Doğruluk oranı: {accuracy:.2f}")
