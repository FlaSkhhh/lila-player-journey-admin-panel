# My Insights



By analyzing the data and player distributions through the dashboard, three distinct patterns emerge that are highly relevant to map flow, AI behavior, and game health.


### Insight 1: Lobby Distributions

* **What caught my eye:** The matchmaking distribution is very weird. Over 95% of the matches contain exactly 1 Human and 0 Bots. Other matches contain 0 Humans and only Bots. As far as I could tell, there are zero instances of multi-human lobbies.
* **The Evidence:** Since I was confused with the distribution, I decided to make a custom player-count UI on the Match ID dropdown. So sweeping through the chronological match list reveals that the vast majority of matches are entirely isolated solo instances.
* **My Thoughts:** Because there are almost 0 PvP encounters, some players might not experience the thrill that they are looking for in an extraction shooter. 


### Insight 2: Bot Pathing vs. Human Pathing

* **What caught my eye:** Bots and Humans traverse the maps in fundamentally different ways, suggesting the AI does not simulate a real human's objective-prioritization.
* **The Evidence:** In the Timeline and Heatmap views, filtering by "Bots Only" shows AI paths being very erratic spreading evenly across map going back and forth between random points. Filtering by "Humans Only" shows the pathway lines straight to the loot/structures especially around the central structures.
* **My Thoughts:** Humans only care about the loot and do not waste any time exploring non loot areas. On the contrary, bots are walking all over the map and are not hyper focused on structures.




### Insight 3: Round/Match Length

* **What caught my eye:** The matches/rounds conclude mostly between 10-15 minutes suggesting that the storm time-limit is around the same time for each game.
* **The Evidence:** By looking at the timeline for the match events, most matches are completed between 10 to 15 minutes from the player dropping in.
* **My Thoughts:** This suggests that humans are not usually killed early and they complete their looting and extraction before the storm closes the map.

