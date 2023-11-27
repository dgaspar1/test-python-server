from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from datetime import datetime
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://denyspg:E7okSR0Pt6huSjHoNkWK0vw9DJ8usdgA@dpg-cl4f0kiuuipc73a7essg-a.ohio-postgres.render.com/tweets_eszd"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class TweetEntity(db.Model):
    __tablename__ = 'tweets'
    id= db.Column(db.INT, primary_key=True)
    text = db.Column(db.TEXT)
    author = db.Column(db.TEXT)
    lemmas = db.Column(db.TEXT)
    polarity = db.Column(db.FLOAT)
    tweetdate = db.Column(db.DATE)
    createdat = db.Column(db.DATE)

class NewAuthors(db.Model):
    __tablename__ = 'newauthors'
    socialnetwork = db.Column(db.TEXT)
    username = db.Column(db.TEXT, primary_key=True)

@app.route('/')
def hello_world():
    return 'Hello, world!'

@app.route('/tweets', methods=['GET'])
def get_tweets():
    tweets = TweetEntity.query.all()
    tweet_list = []
    for tweet in tweets:
        tweet_data = {
            'text': tweet.text,
            'author': tweet.author,
            'lemmas': tweet.lemmas,
            'polarity': tweet.polarity,
            'createdat': tweet.createdat.strftime('%Y-%m-%d %H:%M:%S')
        }
        tweet_list.append(tweet_data)
    return jsonify({'tweets': tweet_list})

@app.route('/new_authors', methods=['GET'])
def get_new_authors():
    new_authors = NewAuthors.query.all()
    author_list = []
    for author in new_authors:
        author_data = {
            'socialNetWork': author.socialnetwork,
            'userName': author.username
        }
        author_list.append(author_data)
    
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://twitter.com/login")
    
    subject = author_list[0]["userName"]
    personTag = "@LulaOficial"

    try:
        with open('authentication.txt', 'r') as auth_file:
            lines = auth_file.readlines()
            username, password = map(str.strip, lines)
    except FileNotFoundError:
        return jsonify({'error': 'Arquivo de autenticação não encontrado'}), 500

    sleep(2)
    usernameField = driver.find_element(By.XPATH,"//input[@name='text']")
    usernameField.send_keys(username)
    next_button = driver.find_element(By.XPATH,"//span[contains(text(),'Avançar')]")
    next_button.click()

    # sleep(3)
    # phoneField = driver.find_element(By.XPATH,"//input[@name='text']")
    # phoneField.send_keys(phone)
    # next_button = driver.find_element(By.XPATH,"//span[contains(text(),'Avançar')]")
    # next_button.click()

    sleep(2)
    passwordField = driver.find_element(By.XPATH,"//input[@name='password']")
    passwordField.send_keys(password)
    log_in = driver.find_element(By.XPATH,"//span[contains(text(),'Entrar')]")
    log_in.click()

    sleep(2)
    search_box = driver.find_element(By.XPATH,"//input[@data-testid='SearchBox_Search_Input']")
    search_box.send_keys(subject)
    search_box.send_keys(Keys.ENTER)

    sleep(2)
    people = driver.find_element(By.XPATH,"//span[contains(text(),'People')]")
    people.click()

    sleep(2)
    profile = driver.find_element(By.XPATH,"//*[@id=\"react-root\"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/section/div/div/div[1]/div/div/div/div/div[2]/div[1]/div[1]/div/div[1]/a/div/div[1]/span/span[1]")
    profile.click()

    sleep(2)
    userTags=[]
    timeStamps=[]
    tweets=[]
    tweetsCount=[]

    userTag = driver.find_element(By.XPATH,"//div[@data-testid='User-Name']").text
    timeStamp = driver.find_element(By.XPATH,"//time").get_attribute('datetime')
    tweet = driver.find_element(By.XPATH,"//div[@data-testid='tweetText']").text
    
    articles = driver.find_elements(By.XPATH,"//article[@data-testid='tweet']")
    print(articles)
    # while len(tweetsCount) < 3:
    for article in articles:
        userTag = article.find_element(By.XPATH, ".//div[@data-testid='User-Name']").text
        isRequired = userTag.find(personTag)
        
        if isRequired > 0:
            sppliteduserTag = userTag.split()
            atUserTag = sppliteduserTag[1]
            userTags.append(atUserTag)
            print(userTag)

            timeStamp = article.find_element(By.XPATH,".//time").get_attribute('datetime')
            timeStamps.append(timeStamp)
            print(timeStamp)
            tweet = article.find_element(By.XPATH,".//div[@data-testid='tweetText']").text
            tweets.append(tweet)
            print(tweet)
        # driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        # sleep(3)
    print("out of loop")
    tweetsCount = list(set(tweets))
    
    # for tweet_text in Tweets2:
    #     new_tweet = TweetEntity(text=tweet_text, author=author_list[0]["userName"], createdat=datetime.now())
    #     db.session.add(new_tweet)
    #     db.session.commit()

    return jsonify({'new_tweets': tweets})

@app.route('/update_polarity', methods=['GET'])
def update_polarity():
    # tweets_without_polarity = Tweet.query.filter(Tweet.polarity == None).all()
    tweets_without_polarity = TweetEntity.query.all()

    for tweet in tweets_without_polarity:
        tweet.polarity = 1
        
    db.session.commit()

    updated_tweets = [
        {
            'id': tweet.id,
            'text': tweet.text,
            'author': tweet.author,
            'lemmas': tweet.lemmas,
            'polarity': tweet.polarity,
            'createdat': tweet.createdat
        }
        for tweet in tweets_without_polarity
    ]

    return jsonify({'tweets_with_updated_polarity': updated_tweets})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=7070)







# import pandas as pd
# df = pd.DataFrame(zip(userTags,timeStamps,Tweets)
#                   ,columns=['userTags','timeStamps','Tweets'])

# df.head()
# df = df.drop_duplicates(subset='Tweets')
# df.to_excel(r"C:\\Users\\Denys\\Documents\\TCC\\polarity-by-author\\natural-language-processing\\data\\data.xlsx",index=False)

# import os
# os.system('start "excel" "C:\\Users\\Denys\\Documents\\TCC\\polarity-by-author\\natural-language-processing\\data\\data.xlsx"')
