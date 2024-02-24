
from fastapi import APIRouter
from database.database import search_embeddings, ingest_embeddings

testrouter = APIRouter(
    prefix='/mytest'
)


@testrouter.get('/')
def testget(mystr: str):
    res = search_embeddings(mystr)
    print(res)
    return mystr


@testrouter.post('/')
def testpost(mystr: str):
    print(mystr)
    res = ingest_embeddings(mystr)
    print(res)
    return mystr



