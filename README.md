# SeifCoin

A simple blockchain built to learn more about blockchain techniques 

To start multiple nodes in the network, pass different ports in the arguments of blockchain.py.
```python
python blockchain.py <port> 
```

For this to work, every node must be aware of the other nodes in the network. This can be done by using a POST request to the following endpoint : 
``` url 
http://<node-ip>:<node-port>/nodes/register
```

The payload structure is: 
``` json
{
    "nodes": ["http://<node-ip>:<node-port>/", "http://<node-ip>:<node-port>/"]
}
```

# Dependencies
- Flask (https://flask.palletsprojects.com/en/2.0.x/)
- Requests (https://pypi.org/project/requests/)
