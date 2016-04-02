# ladder-model
Generate ladder diagrams from a primitive protocol state machine

# Basic usage

~~~
usage: model.py [-h] [--signaling SIGNALING] [--moffset MESSAGE_OFFSET] <file>.json
~~~

Output is in <file>.pdf

You must have groff installed.

Models/state machines look like this.

~~~
{
    "title":"Ordinary RFC 5763",
    "offerer": {
        "START":{
            "report":["starting"],
            "send":[
                "offer"
            ],
            "tstart":[
                "e2e"
            ]
        },
        "answer":{
            "send":[
                "STUN-REQ"
            ]
        },
        "STUN-REQ":{
            "send":[
                "STUN-RESP"
            ]
        },
        "STUN-RESP":{
            "report":["STUN complete"]
        },
        "ClientHello|STUN-RESP":{
            "send":["S1:ServerHello...Finished"]
        },
        "C2":{
            "send":[
                "S2:Finished",
                "Media"    
            ]
        },
        "Media": {
            "tstop":[
                "e2e"
            ]
        }
    },
    "answerer":{
        "offer":{
            "send":[
                "answer",
                "STUN-REQ"
            ],
            "tstart":[
                "e2e"
            ]
        },
        "STUN-REQ":{
            "send":[
                "STUN-RESP"
            ]
        },
        "STUN-RESP":{
            "report":"STUN complete",
            "send":[
                "ClientHello"
            ]
        },
        "S1":{
            "send":[
                "C2:ClientKeyExchange...Finished"
            ]
        },
        "S2":{
            "send":["Media"]
        },
        "Media": {
            "tstop":[
                "e2e"
            ]
        }        
    }
}
~~~


