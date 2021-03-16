# distributed-hash-table

Setup:

* Make sure you are using python 3
* Setup your environment
* Install requirements.txt

```
pip install -r requirements.txt
``` 

First run: 
```
python manager.py
```

Then:

To create the DHT from file
```
python client.py init
```

To list all nodes
```
python client.py list
```

To add a node
```
python client.py join <id>
```

To remove a node
```
python client.py leave <id>
```

To add a shortcut
```
python client.py shortcut <id>:<id>
```
