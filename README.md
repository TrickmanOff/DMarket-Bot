# DMarket-Bot
Bot for auto-targeting and bying skins on DMarket.

[Sample of use (23 May 2020)](https://youtu.be/v5bs3faxc7c)

**NOT WORKING NOW** (apparently because of some changes in site's API or structure)

Set of functions for collecting statistics from the website is written.

# How it works?

Bot looks through all the skins and for each one checks if it is rather popular to be sold quite quickly. 
If it is then bot gets the minimal price with which this skin could be sold.
After this bot adds a profit and fees to this price and sets the target.

It is possible to upgrade this bot for full automatization of target-selling process.

Also it can look at new offers (refreshing them periodically) and check whether it's good for buying: it gets the neccessary statistics about this skin from the site. If it is then bot tries to buy it.
