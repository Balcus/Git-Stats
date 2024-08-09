import requests #type: ignore
from typing import Dict, Any, Union
import pandas as pd #type: ignore
import plotly.express as px #type: ignore
import plotly.io as pio #type: ignore

class API :
    def __init__(self, username : str) -> None:
        self.username = username
        self.headers = {"Accept" : "application/vnd.github.v3+json"}

    def getUserDict(self) -> Union[Dict[str, Any], int] :
        url = f"https://api.github.com/users/{self.username}"
        req = requests.get(url, self.headers)
        if req.status_code == 200:
            user_dict = req.json()
            return user_dict
        else :
            return -1
        
    def getReposDict(self):
        url = f"https://api.github.com/users/{self.username}/repos"
        req = requests.get(url, self.headers)
        if req.status_code == 200 :
            repos_dict = req.json()
            return repos_dict
        else :
            return -1
        
    def makeStarPlot(self, repos_dict):
        repo_links, stars, hover_texts = [], [], []

        for rd in repos_dict :
            repo_name = rd['name']
            repo_url = rd['html_url']
            repo_link = f"<a href = '{repo_url}'>{repo_name}</a>"
            repo_links.append(repo_link)
            stars.append(rd['stargazers_count'])
            owner = rd['owner']['login']
            description = rd['description']
            hover_text = f"{owner} <br />{description}"
            hover_texts.append(hover_text)

        title = f"{self.username}'s Repositories Star Count"
        labels = { 'x' : 'Repository Name' , 'y' : 'Stars'}
        fig = px.bar(x = repo_links, y = stars, title = title, labels = labels, hover_name = hover_texts)
        fig.update_layout(title_font_size = 20, xaxis_title_font_size = 18, yaxis_title_font_size = 18, )
        fig.update_traces(marker_color = 'SteelBlue', marker_opacity = 0.6)
        graph_html = pio.to_html(fig, full_html=False)

        return graph_html
    
    def makeLanguageDistributionPlot(self, repos_dict):
        df = pd.DataFrame(repos_dict)
        df['language'] = df['language'].fillna('Unknown')
        title = "Repository Language Distribution"
        fig = px.pie(df, names='language', values='size', title=title)
        return pio.to_html(fig, full_html=False)
    
    

