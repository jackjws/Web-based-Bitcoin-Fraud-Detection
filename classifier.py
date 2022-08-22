import re

import matplotlib.pyplot as plt
import numpy as np
from graphviz import Source
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.datasets import load_files
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import plot_roc_curve
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import export_graphviz

instance_data = load_files(r"datasets",
                           encoding="utf-8")  # divides dataset into data and target sets
textfiles, filecategories = instance_data.data, instance_data.target  # loads scraped and scams folders into textfiles, target categories are stored in filecategories, a numpy array

params = {'n_estimators': [10, 25, 50, 75, 100, 125, 150, 250],
          'max_depth': [5, 8, 15, 25, 30],
          'min_samples_split': [2, 5, 10, 15, 100],
          'min_samples_leaf': [1, 2, 5, 10]
          }

documents = []

stemmer = WordNetLemmatizer()

for i in range(0, len(textfiles)):
    # removes special characters and symbols
    edit = re.sub(r'\W', ' ', str(textfiles[i]))

    # replaces multiple spaces with single space
    edit = re.sub(r'\s+', ' ', edit, flags=re.I)

    # remove numbers
    edit = re.sub(r'[0-9]', '', edit)

    # removes single characters
    edit = re.sub(r"\b[a-zA-Z]\b", "", edit)

    # converts to Lowercase
    edit = edit.lower()

    # Lemmatization
    edit = edit.split()

    edit = [stemmer.lemmatize(word) for word in edit]
    edit = ' '.join(edit)

    documents.append(edit)

    print("Sanitised Document  " + str(i))

wordVectorizer = CountVectorizer(max_features=7, min_df=0.2, max_df=0.75,
                                 stop_words=stopwords.words('english', 'en'))  # CountVectorize to create features

textfiles = wordVectorizer.fit_transform(documents).toarray()  # fit bag of words into array

feature_names = wordVectorizer.get_feature_names()  # getter for feature names

print("Features determined by CountVectorizer: ", feature_names, "\n")

# convert documents to Term Frequency
tfidfconverter = TfidfTransformer()
textfiles = tfidfconverter.fit_transform(textfiles).toarray()

X_train, X_test, y_train, y_test = train_test_split(textfiles, filecategories, test_size=0.45, random_state=0)

# perform random forest from sklearn
RFclassifier = RandomForestClassifier(n_estimators=50, max_depth=8, min_samples_split=2, min_samples_leaf=1,
                                      random_state=0)

# perform 7 fold cross validation, print the average score
cv = cross_val_score(RFclassifier, X_train, y_train, cv=7, scoring='accuracy') # splits data
print("cross-validation scores: ", cv)
print("%0.2f accuracy with a standard deviation of %0.2f" % (cv.mean(), cv.std()), "\n")

# initialise Gaussian Naive-Bayes
model_G = GaussianNB()

# trains the GNB classifier with the same data
model_G.fit(X_train, y_train)
y_pred_G = model_G.predict(X_test)
cr_G = classification_report(y_test, y_pred_G)

# RFclassifier = GridSearchCV(estimator=RFclassifier, param_grid=params, n_jobs=-1, verbose=3, scoring="neg_mean_squared_error")

RFclassifier.fit(X_train, y_train)  # train the data for random forest

# print(RFclassifier.best_params_)

estimator = RFclassifier.estimators_[5]
 
# predict sentiment
y_pred = RFclassifier.predict(X_test)

print("Random Forest Reports: \n")
print("Confusion Matrix: \n\n", confusion_matrix(y_test, y_pred), "\n")
print("Classification Report: \n", classification_report(y_test, y_pred))
print("Overall accuracy score: ", accuracy_score(y_test, y_pred), "\n")

print('/' * 60, "\n")
print("GNB Reports: \n")
print(cr_G)
print("Number of mislabeled values out of %d points : %d"
      % (X_test.shape[0], (y_test != y_pred).sum()), "\n")

# Export decision tree as dot file
export_graphviz(estimator, out_file='tree.dot',
                feature_names=feature_names,
                class_names=True,
                rounded=True, proportion=False,
                precision=2, filled=True)

s = Source.from_file('tree.dot')
s.view()  # open decision tree visualisation

# plot and display ROC curve for both classifiers
ax = plt.gca() #
RFclassifier_disp = plot_roc_curve(RFclassifier, X_test, y_test, ax=ax, alpha=0.8)
NMBclassifier_disp = plot_roc_curve(model_G, X_test, y_test, ax=ax, alpha=0.8)
plt.plot(ax=ax, alpha=0.8)
plt.show()