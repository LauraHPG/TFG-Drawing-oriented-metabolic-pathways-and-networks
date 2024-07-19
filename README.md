# TDrawing Oriented Metabolic Pathways and Networks

| | Project data |
| ------ | ------ |
| Student | Laura Hui Pérez Guerrero |
| Supervisor | Gabriel Valiente Feruglio  |
| University | Universitat Politècnica de Catalunya, Facultat d'Informàtica de Barcelona |
| Degree | Degree in Informatics Engineering (Computing) |
| Grade | 10 |
| Abstract | This thesis presents an automated tool employing directed hypergraphs to visualize metabolic pathways and networks, enhancing scalability and user interaction in biological data analysis. By converting hypergraphs into traditional graph structures, it enables interactive, customizable network diagrams, facilitating intuitive exploration of complex biochemical data and advancing metabolic network analysis. |

### Installing the requirements :

#### venv and python dependencies

Creating and activating the venv.

On windows

```bash
python -m venv venv
venv\Scripts\activate.bat
```

On Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

Your terminal should look like this

```
(venv) path>
```

Then install the depencies

```bash
pip install -r requirements.txt
```

### Running the Program

The first time you will have to run:

```bash
python manage.py makemigrations
python manage.py migrate
```
You will also have to update the compounds once you load the web page.

Finally:

```bash
python manage.py runserver
```

Open your browser and load this page: http://127.0.0.1:8000/.
