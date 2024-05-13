# Wordle-Game-Bot-Tkinter
Wordle Game implemented in CustomTkinter, in Python. Along with playing Wordle in general, it has a hint generator and it also stores user data on number of games won, on which step the player has won, or if the player has lost a match, it also stores the data.  
&emsp;&emsp; Wordle is a game where the game selects a word randomly from a given set of words of length 5. As the player we have to guess the word within 6 tries. Each time we input a word of length 5. Based on the word we provide, the game gives us a hint. The hint is given in the form that the letters of the word we provided, whether those letters are not in the target word (target word refers to the word selected by the game initially, which the player's trying to guess), if those letters are in the target word, whether they are in the right position or not. For example,  
&emsp;&emsp; If the target word is prior, below is an actual example of an game played by muself. Grey colour represents, the letter is not in the target word. Yellow represents, the letter is in the target word word, but not in the same position as provided by the user. Green represents the letter is in the target word and placed in the correct spot.  
&emsp;&emsp; Here the target word is PRIOR. And we were able to guess that in 3 steps.  
  
![image](https://github.com/NightFury52/Wordle-Game-Bot-Tkinter/assets/143572917/e23bc5ea-3c4b-4c89-916c-8525f69c4f05)  
&emsp;&emsp; There is also a bot in this game, which gives the best possible guess for any step. The Bot doesn't have any idea what's the target word. Given the hints received by the user, the bot gives a list of words which can reduce the size of the list of the remaining possible words (in expectation). This project was motivated by a video on Youtube by the channel name 3Blue1Brown. The link to the video https://youtu.be/v68zYyaEmEA?si=6MoXVl5fpUeQZiAS. Though mine's much simple than that.  

  Hope You'll enjoy :)

