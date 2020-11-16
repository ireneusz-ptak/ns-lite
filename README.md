# NS lite
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

NS lite is an emergency tool useful in case of [Nightscout](http://www.github.com/nightscout/cgm-remote-monitor) failure (i.e. MongoDB issues).
It allows basic remote CGM monitoring until the original app is restored.

## Warning
If you are already hosting your Nightscout app on Heroku be aware that using NS lite at the same time will use your free monthly quota in 20 days.
Make sure you are not using NS lite longer than required.

## Warning2
Current project state: dev completed(?), 0% tests coverage

## Usage
After successful installation you should see a SGV value along with delta and time since last data was received.
If you provided NSLITE_TARGET parameter uploader data (REST API calls at least) will be forwarded to your main Nightscout app so you don't have to switch the uploader configuration back and forth to see if it's working.
NS lite shows only last 3 hours of data and doesn't store it permanently (you'll lose the graph on app restart).

## Installation
1. Fork the ns-lite repository to your Github account (button at the top-right corner).
1. Click "Deploy to Heroku" button on your repository.
1. Login to Heroku.
1. Provide the following information in the form:
   1. Application name (your existing Nightscout name + 'lite' suffix should be enough)
   1. Application location (Europe/USA)
   1. NSLITE_UNITS ('mg/ml' or 'mmol') - currently only mg/ml is supported
   1. NSLITE_TARGET - address of your existing Nightscout page (only host name + port if required i.e. 'mypage.herokuapp.com')
   1. API_SECRET - the same API_SECRET as in your main Nightscout page
1. Create your app.
1. In your uploader tool (i.e. xDrip) provide the NS lite URL in place of your main Nightscout page.
1. Solve your Nightscout problem.
1. Revert the URL in your uploader to the main Nightscout page.
1. Remove NS lite app from your Heroku dashboard (or leave it, but make sure it is suspended after 30 minutes).


## Tech stack
Flask framework (Python) with SQLite in the back, some JS and [uPlot](https://github.com/leeoniya/uPlot) for the graph in front.
