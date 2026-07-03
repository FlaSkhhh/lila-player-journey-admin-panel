# My Insights



By analyzing the data and player distributions through the dashboard, three distinct patterns emerge that are highly relevant to map flow, AI behavior, and game health.


### Insight 1: Lobby Distributions

* **What caught my eye:** The matchmaking distribution is very weird. Over 95% of the matches contain exactly 1 Human and 0 Bots. Other matches contain 0 Humans and only Bots. As far as I could tell, there are zero instances of multi-human lobbies.
* **The Evidence:** Since I was confused with the distribution, I decided to make a custom player-count UI on the Match ID dropdown. So sweeping through the chronological match list reveals that the vast majority of matches are entirely isolated solo instances.
* **Actionable Item & Metrics:** Implement a matchmaking queue threshold to hold the match from starting until some player or time threshold is met. This would increase PvP engagement rate but will also increase the queue time.
* **Why a Level Designer cares:** A map scaled for a multi-player shootout plays completely differently for a solo player. For solo players traversal feels slow and the map feels barren, meaning the designer's intended pacing and combat zones are never experienced. 


### Insight 2: Bot Pathing vs. Human Pathing

* **What caught my eye:** Bots and Humans traverse the maps in fundamentally different ways, suggesting the AI does not simulate a real human's objective-prioritization.
* **The Evidence:** In the Timeline and Heatmap views, filtering by "Bots Only" shows AI paths being very erratic spreading evenly across map going back and forth between random points. Filtering by "Humans Only" shows the pathway lines straight to the loot/structures especially around the central structures.
* **Actionable Item & Metrics:** Adjust the AI pathing to prioritize loot zones. This will in turn increase PvE encounters and will result in higher density of combat events in loot zones.
* **Why a Level Designer cares:** Level Designers need the data for adjusting loot density according to the amount of fights/engagements in the points of interests. If bots are walking all over empty terrain rather than holding down the structures, the data won't help the designer evaluate cover placement, loot quality, or choke points.




### Insight 3: Round/Match Length

* **What caught my eye:** The matches/rounds conclude mostly between 10-15 minutes suggesting that the storm time-limit is around the same time for each game.
* **The Evidence:** By looking at the timeline for the match events, most matches are completed between 10 to 15 minutes from the player dropping in.
* **Actionable Item & Metrics:** Analyze the late-game traversal speed. If players are dying to the storm at near the 15-minute mark, add some traversal help near the perimeter. Doing so can show increase in Successful Extraction Rate and a decrease in Environment-Based Deaths.
* **Why a Level Designer cares:** This suggests that humans are surviving early PvP/PvE, but tells the designer exactly how much time players need to complete their looting cycle. It allows them to tune the physical distance between high-tier loot zones and extraction points so it perfectly matches the 15-minute storm timer.

