import requests


OSU_CLASS_API = "https://content.osu.edu/v2/classes/search?q="

response = requests.get(f"{OSU_CLASS_API}")
print(response.json())