from flask import Flask, render_template, url_for, request #type: ignore
from API import API

app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        api = API(username)
        user_dict = api.getUserDict()
        repos_dict = api.getReposDict()
        if user_dict == -1: 
            return render_template('index.html', error="The user does not exist")
        elif repos_dict == -1:
            return render_template('index.html', error="Couldn't retrieve user's repository data")
        elif not repos_dict:
            return render_template('index.html', error="We did not find any public repositories")
        
        star_graph = api.makeStarPlot(repos_dict)
        language_distribution_graph = api.makeLanguageDistributionPlot(repos_dict)
        return render_template('index.html', user=user_dict, repos=repos_dict, star_plot=star_graph, language_plot = language_distribution_graph)
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
