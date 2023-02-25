# SaveTweets
Archive tweets using the Internet Archive API.

## Installation
```
pip3 install git+https://github.com/nisotsu/SaveTweets.git
```
## Usage
Create an Internet Archive account and get API keys.

You can get your API key [here](https://archive.org/account/s3.php).

```
usage: savetweets [-h] [--likecount LIKECOUNT] [--replycount REPLYCOUNT]
                        [--retweetcount RETWEETCOUNT] [--quotecount QUOTECOUNT] [--nocheck]
                        id
```
```
positional arguments:
  id                    Twitter ID you want to archive.

options:
  -h, --help            show this help message and exit
  --likecount LIKECOUNT
                        Archive only tweets with more likes than specified number.
  --replycount REPLYCOUNT
                        Archive only tweets with more replies than specified number.
  --retweetcount RETWEETCOUNT
                        Archive only tweets with more retweets than specified number.
  --quotecount QUOTECOUNT
                        Archive only tweets with more quotes than specified number.
  --nocheck             Do not check if archived successfully.
```

### Examples
Archive all tweets from @internetarchive.
```
savetweets internetarchive
```
Only archive tweets with more than 1000 likes.
```
savetweets internetarchive --likecount 1000
```
Only archive tweets with more than 1000 likes and more than 500 retweets.
```
savetweets internetarchive --likecount 1000 --retweetcount 500
```