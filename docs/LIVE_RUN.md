# Last live ingestion run (UFCStats)

Written by the workflow `live-ingestion.yml` on a GitHub-hosted runner. Run: https://github.com/brianphu2310/UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE/actions/runs/37233562364

- Run at (UTC): 2026-10-04T20:49:29Z

## First rows

## Source probe
```
HTTP/1.1 200 OK
Server: nginx/1.10.1
Vary: Accept-Encoding
Cache-Control: no-store, no-cache, must-revalidate
Content-Type: text/html; charset=utf-8
Date: Sun, 04 Oct 2026 20:47:01 GMT
Status: 200 OK
Pragma: no-cache
X-XSS-Protection: 1; mode=block
Transfer-Encoding: chunked
X-Content-Type-Options: nosniff
Connection: Keep-Alive
X-Frame-Options: SAMEORIGIN

<!doctype html><html><head><meta charset="utf-8">
<title>Loading…</title><meta name="robots" content="noindex">
<style>body{font-family:sans-serif;color:#666;text-align:center;margin-top:25vh}</style>
</head><body>
<p>Checking your browser…</p>
<noscript>This site requires JavaScript.</noscript>
<script>
(function(){
var K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
function ror(x,n){return (x>>>n)|(x<<(32-n));}
function sha256(msg){
  var bytes=[];for(var i=0;i<msg.length;i++){
    var c=msg.charCodeAt(i);
    if(c<128){bytes.push(c);}
    else if(c<2048){bytes.push(192|(c>>6),128|(c&63));}
    else{bytes.push(224|(c>>12),128|((c>>6)&63),128|(c&63));}
  }
  var l=bytes.length;bytes.push(0x80);
  while((bytes.length%64)!==56)bytes.push(0);
```

## Run log (tail)
```
2026-10-04 20:49:28,325 DEBUG urllib3.connectionpool: Starting new HTTP connection (1): ufcstats.com:80
2026-10-04 20:49:28,495 DEBUG urllib3.connectionpool: http://ufcstats.com:80 "GET /robots.txt HTTP/1.1" 404 18
2026-10-04 20:49:29,836 DEBUG urllib3.connectionpool: http://ufcstats.com:80 "GET /statistics/fighters HTTP/1.1" 200 None
2026-10-04 20:49:29,837 INFO ingestion.fetch: fetched http://ufcstats.com/statistics/fighters (2994 chars)
2026-10-04 20:49:29,838 WARNING ingestion.ufcstats: no fighter table on page 1; stopping
2026-10-04 20:49:29,838 ERROR ingestion.ufcstats: no rows scraped; nothing written
```
