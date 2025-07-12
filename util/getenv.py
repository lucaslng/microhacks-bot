import os

def getenv(key: str) -> str:
	value = os.getenv(key)
	assert value
	return value