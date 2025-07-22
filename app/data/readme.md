All the data from JSON files should be added to a question quiz.

The format of the JSON should be:

```json
[
    {
        "statement": "Question",
        "answer": "Right answer",
        "options": ["option 1", "Right answer", "option 2", "option 3"]
    }
]
```

Example prompt in Spanish for generating quiz questions from data

```
dame una lista de 50 preguntas, respuesta y opciones según la siguiente estructura, con el tema de películas de ciencia ficción

{
    "statement": "pregunta",
    "answer": "respuesta",
    "options": ["opcion1", "opcion1", "opcion3"]
}


```