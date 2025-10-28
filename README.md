## How to setup

```
git clone https://github.com/Pikalot/Web-Robot
cd 'Web-Robot'
python -m venv venv
```

**Create a .env file in the project root:**

```
WEB-ROBOT/
├── _pycache_/
├── venv/
├── .env
├── .gitignore
├── llm_model.py
├── main.py
├── README.md
└── requirements.txt
```

**Inside your .env file, add:**

```
OPENAI_API_KEY=your_openai_api_key_here
BROWSER=your_browser
```

**Activate the virtual environment:**

- Windows: ``` venv\Scripts\activate ```
- Mac/Linux: ``` source venv/bin/activate ```

_You should see (venv) appear at the start of the terminal line._

### Install dependencies
```
pip install -r requirements.txt
```

### (Optional) Manual installation
**Install Playwright**

```
pip install playwright
playwright install
```

**Install OpenAI**

```
pip install openai
pip install python-dotenv
```

## How to run

```
python main.py
```
