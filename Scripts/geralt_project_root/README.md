**Propósito:**

* El módulo atm_segmentation.ipynb debe ser capaz de regresar una cantidad determinada **N** de cajeros de un tipo de pre-cluster existente *(actualmente son 4 20/02/2026)*. Dicha consulta debe respetar la siguiente estrcutura:
*Pedimento por: 


| Pre-cluster        | Porcentaje (%) | Número (n) |
|--------------------|---------------:|-----------:|
| NORMAL_ESTABLE     | XX.X%          | XXXX       |
| EVENT_DRIVEN       | XX.X%          | XXXX       |
| NORMAL_CON_PICOS   | XX.X%          | XXXX       |
| GRANDE_Y_ESTABLE   | XX.X%          | XXXX       |

inicialmente debe devolver los ATM en una lista para cada tipo de  pre-cluster. 
Se puede hacer pedimento de al menos un tipo de pre-cluster de los $m$ disponibles (en este momento $m=4$), o de $m$ por consulta. Si en una ejecución $m$-$s$ $($s$=$1$,$2$,$3$)$, solo se generará una lista de los $m-s$ seleccionados, para evitar listas vacías.


---
Preguntas:

- ¿Es posible que un cajero pertenezca a un pre-cluster en un parket, pero en otro momento pertenezca a otro dado un nuevo parket?
  De ser así ¿Qué tan probable es?, ¿Qué tan grave es el efecto tiene sobre la inferencia? y ¿Cómo solventarlo?


