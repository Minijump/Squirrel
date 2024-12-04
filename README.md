# Squirrel (Mvp)
      
Create data analysis pipeline by generating python with a low-code interface. 
## The app
### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/Minijump/Squirrel.git
    cd Squirrel
    ```

2. **Create a virtual environment (optional):**
    * Create the environment
        ```sh
        python -m venv venv_name
        ```
    * Activate it

        windows:
        ```sh
        .\venv_name\Scripts\activate
        ```

        Linux:
        ```sh
        source venv/bin/activate
        ```
    Note that real cowboys do not bother with v-envs and deal with problems such as conflicts when they appears. 

3. **Install the required Python packages:**
    ```sh
    pip install -r requirements.txt
    ```

### Running the Application

1. **Install a server**

    Uvicorn is not mandatory, feel free to use whatever can do the job.

    ```sh
    pip install uvicorn
    ```

2. **Start the FastAPI server:**
    ```sh
    uvicorn app.main:app
    ```
    Note that you will often see this command with '--reload' argument. Do not use it to run the app, it will cause troubles when the pipeline.py file is updated.

3. **Open your browser and navigate to:**
    ```
    http://127.0.0.1:8000
    ```

### Usage

1. **TODO: pitcures, main concepts, ...**


## Develoment

### Customize

1. **TODO main structure(decorator,...), manifest,...**

### Running Tests

1. **Run the unit tests:**
    ```sh
    pytest ./tests
    ```
### Contributing

1. **Fork the repository**
2. **Create a new branch:**
    ```sh
    git checkout -b feature/your.feature.name
    ```
    Words of your features must be separated by dots, feel free to add version number, github username, ... before or after the feature name (expl: 2.1.1-feature.name-github_username)
3. **Make your changes and commit them:**
    ```sh
    git commit -m 'Add a meaningfull commit message'
    ```
    Fixed commit messages conventions are for nazis, yet, beeing meanigfull and complete is a must. 
4. **Push to the branch:**
    ```sh
    git push origin feature/your.feature.name
    ```
5. **Create a new Pull Request**

### To do MVP
* Data sources: create API sources, change structure (to work with API + correct edit source), at creation: standard pop up than custom one?, create multiple source types 
* Table: change structure, enable to do wathever you want with python (delete lines where -, Data export (csv), ...)
* Complete README + Demo project

### To do
* Odoo module: ease import process
* Do not run all pipeline at each actions (and for pager, infos, ...)
* Features ideas: great-expectations unit test, API connection to diff services, Excel functions copy, see what would change if you do an action, see what changed at each action (run a script on pipeline + see diffs), git/github integrations, multiple pipelines, export as jupyter ...
* ...
