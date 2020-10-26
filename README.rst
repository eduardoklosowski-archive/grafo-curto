===========
Grafo Curto
===========

API Web para buscar o menor caminho entre dois vértices de um grafo.

Exemplo
=======

Executar servidor:

.. code-block:: sh

   python grafo.py

Fazer requisição:

.. code-block:: sh

   http :8000 graph:=@content source=a destination=b

Requisição
----------

.. code-block:: json

   {
     "source": "a",
     "destination": "b",
     "graph": {
       "vertexes": [
         {"id": "a", "name": "a"},
         {"id": "b", "name": "b"}
       ],
       "edges": [
         {"id": 1, "source": "a", "destination": "b", "weight": 2},
         {"id": 2, "source": "a", "destination": "b", "weight": 1}
       ]
     }
   }

Resposta
--------

.. code-block:: json

   {
     "source": "a",
     "destination": "b",
     "has_path": true,
     "path": [
       {"id": 2, "source": "a", "destination": "b", "weight": 1}
     ],
     "cost": 1
   }
