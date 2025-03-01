resources -> https://stackoverflow.com/questions/76322463/how-to-initialize-a-global-object-or-variable-and-reuse-it-in-every-fastapi-endp
https://gist.github.com/nicksonthc/525742d9a81d3950b443810e8899ee0e

### Design Plan
1. pinging api whenever I am coming online and offline
Problem -> server overload and saving to db will lead to crashing

2. lets have a cache in place. Whenever an user is coming online
save it to the db and then to the cache. 
Then users can easily query whether other users are online/offline.
First hit will be made to the cache.
problem -> we can't keep the user forever in the cache. We need to clear off
the offline state cache

3. TTL + hearbeat. If came online put the user in the online state in the cache. with ttl of 
5mins.  
So atleast an offset of 5mins will be there like we have in insta.
What if I am still online? Let the client send a heartbeat every 30 seconds.
So even if the user is having network issues , he will get offline eventually

cache miss -> offline
no hitting to the main db as we dont need to save for long term.
online/offline is just an indication
problem -> cant show "last seen at 12:15pm"

4. solution -> event listener of ttl expiry.
user offline -> consumer -> update the db
problem -> what if a lot of events come at once?

5. solution -> snapshot based. At every 5 mins. Run a script to scan the cache and track all users online

Last problem -> not instant and majorly eventually consistent