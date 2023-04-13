# Bomberman-game
To run this code correctly you need Python 3.x and libraries: PyQt5, random, heapq, PyQt5.QtGui, PyQt.QtWidgets and PyQt.QtCore. <br />
<br />
You can control player by using arrow keys on you keboard or by pressing on the player and dragging it to the place you want him to go. It will find the shortest way if one exists and player will move to destination. <br />
Placing the bombs happen by pressing Space key. If player collects and activates "detonator" powerup, detonation of the bomb happens by pressing "B" key. <br />
When powerup is collected it disappears from the board and appears above it. You can activate collected powerup by clicking on it. When powerup is clicked again, it deactivates. Only one powerup can be active at a time. <br />
Game has following powerups: <br />
![alt text](https://cdn.wikimg.net/en/strategywiki/images/e/e4/Bomberman_Bombs.png) Bombs - everytime it is collected, it increases amount of bombs placed at a time. <br />
![alt text](https://cdn.wikimg.net/en/strategywiki/images/e/e4/Bomberman_Flames.png) Flames - everytime it is collected it increases the explosion range by 1. <br />
![alt text](https://cdn.wikimg.net/en/strategywiki/images/e/e4/Bomberman_Speed.png) Speed - increases player's speed by 2. <br />
![alt text](https://cdn.wikimg.net/en/strategywiki/images/e/e4/Bomberman_Wallpass.png) Wallpass - allows player to move through the destructible walls. <br />
![alt text](https://cdn.wikimg.net/en/strategywiki/images/e/e4/Bomberman_Detonator.png) Detonator - allows player to detonate a bomb by pressing "b". <br />
![alt text](https://cdn.wikimg.net/en/strategywiki/images/e/e4/Bomberman_Bombpass.png) Bombpass - allows player to move through bombs. <br />
![alt text](https://cdn.wikimg.net/en/strategywiki/images/e/e4/Bomberman_Flamepass.png) Flamepass - makes player immune to explosions. <br />
![alt text](https://cdn.wikimg.net/en/strategywiki/images/e/e4/Bomberman_Mystery.png) Mystery - makes player immune to monsters and explosions. <br />
Game is over when player is touched by enemy or harmed in explosion. <br />
Game is won when player destroys all of the enemies and stands next to the door. <br />
