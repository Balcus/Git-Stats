import requests #type: ignore
from typing import Dict, Any, Union
import pandas as pd #type: ignore
import plotly.express as px #type: ignore
import plotly.io as pio #type: ignore
from datetime import datetime
import pytz #type: ignore

class API :
    def __init__(self, username : str, token : str = None) -> None:
        self.username = username
        self.token = token
        self.headers = { "Accept" : "application/vnd.github.v3+json"}
        if token and len(token) == 40 :
            self.headers["Authorization"] = f"token {self.token}"
            print(self.headers)

    def fetchUserDict(self) -> Union[Dict[str, Any], List[Union[int, str]], None]:
        url = f"https://api.github.com/users/{self.username}"
        response = requests.get(url, self.headers)
        if response.status_code == 200:
            user_dict = response.json()
            return user_dict
        elif response.status_code == 403:
            if 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
                reset_time = int(response.headers['X-RateLimit-Reset'])
                reset_time_human = datetime.fromtimestamp(reset_time, tz=pytz.timezone('Europe/Bucharest')).strftime('%Y-%m-%d %H:%M:%S')
                return [-1, reset_time_human]
        else :
            return None
        
    def fetchReposDict(self) -> Union[List[Dict[str, Any]], List[Union[int, str]], None]:
        url = f"https://api.github.com/users/{self.username}/repos"
        response = requests.get(url, self.headers)
        if response.status_code == 200 :
            repos_dict = response.json()
            return sorted(repos_dict, key=lambda repo : repo['created_at'])
        elif response.status_code == 403:
            if 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
                reset_time = int(response.headers['X-RateLimit-Reset'])
                reset_time_human = datetime.fromtimestamp(reset_time, tz=pytz.timezone('Europe/Bucharest')).strftime('%Y-%m-%d %H:%M:%S')
                return [-1, reset_time_human]
        else :
            return None
        
    def fetchEvents(self) -> Union[List[Dict[str, Any]], List[Union[int, str]], None]:
        url = f"https://api.github.com/users/{self.username}/events"
        events = []
        while url:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                events.extend(response.json())
                url = response.links.get('next', {}).get('url')
            elif response.status_code == 403:
                if 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
                    reset_time = int(response.headers['X-RateLimit-Reset'])
                    reset_time_human = datetime.fromtimestamp(reset_time, tz=pytz.timezone('Europe/Bucharest')).strftime('%Y-%m-%d %H:%M:%S')
                    return [-1, reset_time_human]
            else:
                return None
        return events
    
    def fetchCommits(self, owner: str, repo: str) -> Union[List[Dict[str, Any]], List[Union[int, str]], None]:
        commits = []
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?author={self.username}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200 :
            commits.extend(response.json())
            return commits
        elif response.status_code == 403:
            if 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
                reset_time = int(response.headers['X-RateLimit-Reset'])
                reset_time_human = datetime.fromtimestamp(reset_time, tz=pytz.timezone('Europe/Bucharest')).strftime('%Y-%m-%d %H:%M:%S')
                return [-1, reset_time_human]
        else :
            return None
    
        
    def makeStarPlot(self, repos_dict: List[Dict[str, Any]]) -> str:
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
    
    def getTotalStars(self, repos_dict: List[Dict[str, Any]]) -> int:
        stars = 0
        for rd in repos_dict :
            stars += rd['stargazers_count']
        return stars
    
    def makeLanguageDistributionPlot(self, repos_dict: List[Dict[str, Any]]) -> str:
        df = pd.DataFrame(repos_dict)
        df['language'] = df['language'].fillna('Unknown')
        title = "Repository Language Distribution"
        fig = px.pie(df, names='language', values='size', title=title)
        return pio.to_html(fig, full_html=False)
    
    def extractContributions(self, events: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        contributions = []
        for event in events:
                event_date = event['created_at'].split('T')[0]
                contributions.append(dict(Task=f"{event['type']}", Date=f"{event_date}"))
        return contributions
    
    def makeActivityMap(self, contributions: List[Dict[str, str]]) -> str:
        df = pd.DataFrame(contributions)
        df['Date'] = pd.to_datetime(df['Date'])
        
        fig = px.scatter(
            df, 
            x="Date", 
            y="Task", 
            color="Task", 
            title="Scatter Plot of Activities Over Time",
            labels={"Task": "Activity Type", "Date": "Date"}
        )
        
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Activity Type',
            xaxis=dict(
                tickformat="%Y-%m-%d",  
                tickangle=45  
            ),
            yaxis=dict(
                categoryorder="total ascending"  
            ),
            showlegend=False  
        )
        
        return pio.to_html(fig, full_html=False)
    
    def getFirst100StarRepo(self, repos_dict: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        for rd in repos_dict :
            if rd['stargazers_count'] >= 100 :
                return rd
        return None
    
    def getFirstForkRepo(self, repos_dict: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        for rd in repos_dict :
            if rd.get('fork') is True :
                return rd
        return None
    
    def getFirstCollaboration(self, repos_dict: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        for rd in repos_dict:
            pr_url = f"https://api.github.com/repos/{self.username}/{rd['name']}/pulls?state=all&sort=created&direction=asc"
            pr_response = requests.get(pr_url, headers=self.headers)
            
            if pr_response.status_code == 200:
                pull_requests = pr_response.json()
                for pr in pull_requests:
                    if pr['user']['login'] != self.username:
                        return [rd, pr]
        return None
    
    def getEmployment(self, user_dict: Dict[str, Any]) -> Optional[str]:
        if user_dict['company'] != 'Not specified' :
            return user_dict['company']
        return None
    
    def getCommitNumber(self, repos_dict: List[Dict[str, Any]]) -> int:
        total_commits = 0
        for rd in repos_dict :
            owner = rd['owner']['login']
            repo_name = rd['name']
            commits = self.fetchCommits(owner, repo_name)   
            total_commits += len(commits)

        return total_commits


        
        

