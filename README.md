# the-pattern-api
API gateway for The Pattern 

- [] add parsed date as int into nodes
- [x] add titles to edge api endpoint and edgeview

# Quickstart 

assuming you have redisgraph on localhost 9001 

pip install -r requirements.txt 

python app.py 


validate

```
curl -i -H "Content-Type: application/json" -X POST -d '{"search":"laser correction operation"}' http://127.0.0.1:8181/search
Access-Control-Allow-Origin: *
Server: Werkzeug/1.0.1 Python/3.8.5
Date: Thu, 31 Dec 2020 06:30:39 GMT

{"search_result":{"links":[{"source":"C5162902","target":"C5141303"},{"source":"C5162902","target":"C5191700"},{"source":"C5141303","target":"C5191700"}],"nodes":[{"id":"C5162902","name":"C5162902"},{"id":"C5141303","name":"C5141303"},{"id":"C5191700","name":"C5191700"}]}}
```

```
curl -X GET "http://127.0.0.1:8181/edge/edges:C5143452:C5119559"
{
  "results": [
    {
      "sentence": null, 
      "sentencekey": "sentences:PMC7112304.xml:132", 
      "title": null
    }
  ]
}
```
Populate titles 

```
python IntakeRedis_titles.py
```
Re-run: 

```
curl -X GET "http://127.0.0.1:8181/edge/edges:C5143452:C5119559"
{
  "results": [
    {
      "sentence": null, 
      "sentencekey": "sentences:PMC7112304.xml:132", 
      "title": "Common Features of Enveloped Viruses and Implications for Immunogen Design for Next-Generation Vaccines"
    }
  ]
}
```

Currently titles are using standard SET operation which results in ~1 GB RAM, changing it to hset most likely will save memory. 
