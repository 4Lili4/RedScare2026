## Repository structure
```
├── forked_data   #folder containing the data for all the graphs. We use these in all_code_runnable.ipynb
│   ├── bht.txt
│   ├── common-1-1000.txt
│   ├── ...
│   ├── wall-z-3.txt
│   └── wall-z-4.txt
├── forked_doc   #unchanged and unused from https://github.com/thorehusfeldt/algdes-labs/tree/master/red-scare
│   └── ...
├── forked_instance-generators   #unchanged and unused from as forked_doc
│   └── ...
├── results   #folder containing descriptive and timed results for each problem
│   ├── 01_alternate.csv
│   ├── 02_few.csv
│   ├── 03_many.csv
│   ├── 04_none.csv
│   └── 05_some.csv
├── visualisations for Some   #folder containing a script for visualising the Some-algorithm
│   ├── SomeViz.html
│   ├── SomeViz.md
│   └── SomeViz.py
├── all_code_runnable.ipynb   #main notebook
├── AlternateProblem.py
├── env.yml   #Conda environment-file
├── FewProblem.py
├── ManyProblem.py
├── NoneProblem.py
├── README.md   #this file :-) 
├── req.txt   #pip environment-file
├── results.txt   #results.txt following the format requested in algdes-labs/.../report.pdf
└── SomeProblem.py
```

# How to recreate our results

## RedScare environment
In your preferred terminal, navigate to this repository. Then choose between the following:

### Creating an environment with Conda
paste the following into your terminal window and run the command:
``` 
conda env create -f env.yml
conda activate RedScare_grpV
```

### Creating an environment with pip
Requires Python 3.11+

#### Windows (PowerShell)
paste the following into your terminal window and run the command:
```
py -m venv .venv 
.venv\Scripts\Activate.ps1
pip install -r req.txt
```
#### Windows (command prompt)
paste the following into your terminal window and run the command:
```
py -m venv .venv 
.venv\Scripts\Activate.bat
pip install -r req.txt
```

#### macOS / Linux (bash)
paste the following into your terminal window and run the command:
``` 
python -m venv .venv
source .venv/bin/activate
pip install -r req.txt
```
_______________________________________________
Once you have created and activated the environment, you can run the code.

## Running the code
Once you have created and activated the RedScare-environment, all our code is runnable through one neat notebook via function imports.
Each problem is solved with functions in a .py file named for the problem it solves. The functions from these files are then imported in the **master_notebook.ipynb**, making everything run smoothly from this one notebook. The file can be run from start to finish, and will automatically recreate **results.txt** as well as the more detailed files in **/results/**.
