deribit-api
===========
Deribit API python playground

### introduction
This repository contains a class to abstract some of the API interactions and an interactive notebook making it easier to adapt the code to your needs. Simple API endpoint usage has been implemented and a more complex function that circumvents the pagination limitation of the `trades` api and returns a full result of trades within a given timeframe.

The notebook additionally has an interactive cell allowing you to save trades of a specific instrument within a timeframe to csv.

### instructions

1. Get your environment setup with Python, Jupyter Lab and the required dependencies `jupyterlab` `pandas` etc. There are various tutorials on the internet to get this working on your environment (make sure you do it within a virtual environment as it will prevent pollution of your host).
2. Run `jupyter lab` within the folder of this code so you can interactively run the notebook.
3. Execute the cells, inspect results, it should be relatively self explanatory.
