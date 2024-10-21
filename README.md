# Image Editing Agent Workshop

![Replace the horse by a cow](teaser.png)

Welcome to our AI agent Workshop! We'll go through the process of designing an image editing agent that can replace a horse by a cow based on natural language instructions.

## Prerequisites
- Python 3.10+
- OpenAI API key

## Installation
1. Clone this repository:
   ```
   git clone https://github.com/yefan/image-agent-workshop.git
   ```
2. Install dependent libraries in a virtual environment:
   If you have `venv` already installed, create a new virtual environment:
   ```
   python -m venv venv
   ```
   If you are running into error because venv is not yet installed, you can install it using `pip`
   ```
   pip install virtualenv
   ``` 
3. Activate the virtual environment
   - On Windows:
      ```
      .\venv\Scripts\Activate.ps1
      ```
   - On macOS and Linux:
      ```
      source venv/bin/activate
      ```
4. Install the dependencies through pip:
   ```
   pip install -r requirements.txt
   ```
3. Add your OpenAI API key to the `.env` file:
    `.env` file stores environment variables that can be loaded by the `dotenv` library. Typically this file is kept private, and not checked in to a repo. There's a `.env.example` file, which you can make a copy from, and replace the API key in that file by your own key. 

## Running the code
```
cd Exercise1/1/a
python tools.py
```
If not running into errors, then you are all set. Start hacking! 
