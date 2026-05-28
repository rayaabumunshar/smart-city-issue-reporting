from functools import lru_cache

import redis
from influxdb_client import InfluxDBClient
from neo4j import GraphDatabase
from pymongo import MongoClient

from backend import config


@lru_cache(maxsize=1)
def get_mongo_client():
    return MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=3000)


def get_mongo_db():
    return get_mongo_client()[config.MONGO_DB_NAME]


@lru_cache(maxsize=1)
def get_neo4j_driver():
    return GraphDatabase.driver(
        config.NEO4J_URI,
        auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
    )


@lru_cache(maxsize=1)
def get_redis_client():
    client = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )
    client.ping()
    return client


@lru_cache(maxsize=1)
def get_influx_client():
    return InfluxDBClient(
        url=config.INFLUX_URL,
        token=config.INFLUX_TOKEN,
        org=config.INFLUX_ORG,
        timeout=3000,
    )


def get_influx_write_api():
    return get_influx_client().write_api()


def get_influx_query_api():
    return get_influx_client().query_api()

