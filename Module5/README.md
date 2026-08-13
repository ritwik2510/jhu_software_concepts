Setup Instructions

1. Install dependencies:
pip install -r requirements.txt
2. Set up PostgreSQL database:
Create a database named gradcafe.
3.Run the flask application
use python -m src.app

4.Run full test with pytest after creating markers with pytest.ini 

5. Run Sphinx with
sphinx-build and then where you want it to be located
6. Open website 
website is located at index.html (for example: file:///C:/Users/ritwi/Documents/Modern%20Python/jhu_software_concepts/Module4/docs/build/html/index.html)

Notes/Bugs and Issues
Could only get 76% completion through pytest
Sphinx autodoc would not pull from the modules and ended up being blank for those parts