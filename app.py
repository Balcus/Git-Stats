from flask import Flask, render_template, url_for, request #type: ignore
from API import API

app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        token = request.form.get('token')

        if not username or not token:
            return render_template('index.html', error="Username required.")
        
        api = API(username, token)
        user_dict = api.fetchUserDict()
        repos_dict = api.fetchReposDict()
        events_dict = api.fetchEvents()

        if events_dict :
            contributions = api.extractContributions(events_dict)

        if not user_dict :
            return render_template('index.html', error="Couldn't retrieve user's data")
        elif not repos_dict :
            return render_template('index.html', error="Couldn't retrieve repository data")
        
        if isinstance(user_dict, list) and user_dict[0] == -1:
            return render_template('index.html', error=f"You've hit the rate limit for GitHub API requests. Please try again : {user_dict[1]} (Europe/Romania Time Zone). To increase your rate limit, consider adding a GitHub token.")

        if isinstance(repos_dict, list) and repos_dict[0] == -1:
            return render_template('index.html', error=f"You've hit the rate limit for GitHub API requests. Please try again : {repos_dict[1]} (Europe/Romania Time Zone). To increase your rate limit, consider adding a GitHub token.")

        if events_dict and isinstance(events_dict, list) and events_dict[0] == -1:
            return render_template('index.html', error=f"You've hit the rate limit for GitHub API requests. Please try again : {events_dict[1]} (Europe/Romania Time Zone). To increase your rate limit, consider adding a GitHub token.")
        
        if events_dict:
            contributions_plot = api.makeActivityMap(contributions)
        else :
            contributions_plot = None
        star_plot = api.makeStarPlot(repos_dict)
        total_stars = api.getTotalStars(repos_dict)
        language_distribution_plot = api.makeLanguageDistributionPlot(repos_dict)
        first100stars = api.getFirst100StarRepo(repos_dict)
        firstFork  = api.getFirstForkRepo(repos_dict)
        firstCollab = api.getFirstCollaboration(repos_dict)
        employed = api.getEmploymnet(user_dict)
        total_commits = api.getCommitNumber(repos_dict)

        return render_template('index.html', 
                               user=user_dict, 
                               repos=repos_dict, 
                               star_plot=star_plot, 
                               total_stars = total_stars, 
                               language_plot = language_distribution_plot,
                               contributions_plot = contributions_plot,
                               first100stars = first100stars,
                               firstFork = firstFork,
                               firstCollab = firstCollab,
                               employed = employed,
                               total_commits = total_commits)
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
