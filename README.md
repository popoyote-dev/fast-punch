# Fast Punch

##### Quizz Game

Faster response give more point, random question on every game.


Copy a json files with questions in ```app/data```
``` json

{
    "statement": "Question",
    "answer": "answer",
    "options": ["answer", "opcion1", "opcion1", "opcion3"]
}

```

##### Install dependencies

``` bash 
make install
```

##### Run local

``` bash
make run
```


#### Avatars
Add avatars images to a folder ```app/static/avatars```

#### User

Go to the root path of your server domain.

Example (local server):
> http://localhost:8000/

#### Admin

Go to the config path to personalize the quiz.

Example (local server):
> http://localhost:8000/admin/
