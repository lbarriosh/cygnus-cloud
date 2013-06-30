Readme (Spanish version)
========================

Breve descripción del proyecto
------------------------------
CygnusCloud es un proyecto de fin de carrera desarrollado por Luis Barrios, Adrián Fernández y Samuel Guayerbas,
alumnos de Ingeniería Informática de la Universidad Complutense de Madrid.

El objetivo de CygnusCloud es convertir las aulas de informática no especializadas repartidas por todo el campus 
en laboratorios de informática. Esto permitirá a los estudiantes poder realizar las prácticas
de sus asignaturas fuera de las sobreutilizadas aulas de informáticas especializadas de sus correspondientes facultades.

Además, CygnusCloud ofrece otros beneficios:
* Ahorro de costes. Es posible utilizar ordenadores más baratos y con un consumo eléctrico inferior.
* Menos burocracia. Hoy en día, si un profesor quiere instalar un programa específico para la realización
  de alguna de sus prácticas, tendrá que esperar al menos un mes para poder disponer de dicho programa.
  Con CygnusCloud los profesores podrán instalar aplicaciones directamente en sus propias máquinas virtuales,
  y dar acceso a ellas en pocas horas.

Licencia
--------
* Toda la documentación de CygnusCloud está publicada bajo una licencia Creative Commons 
  Atribución-NoComercial-CompartirIgual 3.0 Unported. El texto de la licencia puede consultarse en
  http://creativecommons.org/licenses/by-nc-sa/3.0/deed.es.
* La versión modificada de noVNC se distribuye bajo la Licencia Pública Mozilla, versión 2.0. Su texto completo
  puede consultarse en http://www.mozilla.org/MPL/2.0/.
* El resto de código de CygnusCloud se distribuye bajo la licencia Apache, versión 2. Su texto completo
  puede consultarse aquí: http://www.apache.org/licenses/LICENSE-2.0.html.

Cómo descargar e instalar CygnusCloud
-------------------------------------
Actualmente, puede descargarse la versión 5.0.1 de CygnusCloud desde la página de descarga de nuestro blog 
(http://cygnusclouducm.wordpress.com/descargas-v5-0-1/).
Las instrucciones de instalación y uso
se describen en la memoria del proyecto (disponible en http://cygnusclouducm.files.wordpress.com/2013/06/memoria.pdf).

Árbol de directorios
--------------------
Los principales directorios que podemos encontrar en el repositorio de CygnusCloud son:

* Arquitectura: incluye un conjunto de documentos escritos durante el desarrollo del proyecto
 con los diseños preliminares de la arquitectura realizados.
* Documentación interna:  incluye un conjunto de manuales escritos por nosotros que explican de forma
      sencilla cómo instalar y utilizar las diferentes herramientas utilizadas en el desarrollo del proyecto.
* Memoria: incluye el código fuente de la memoria del proyecto. En ella, se define de forma 
  detallada todos los aspectos relacionados con CygnusCloud. Toda la memoria se encuentra escrita en LaTeX
  usando LyX, siendo "Memoria.lyx" el fichero principal. 
* src: incluye todo el código fuente de la última versión estable. En su interior podemos
  destacar dos subdirectorios relevantes: src/Infraestructura (incluye todo el código relacionado con los servidores de máquinas virtuales y 
	  el servidor de cluster) y src/web (incluye todo el código relacionado con el servidor web).

Documentación
-------------
La memoria del proyecto (disponible en http://cygnusclouducm.files.wordpress.com/2013/06/memoria.pdf) incluye
el diseño detallado de CygnusCloud y su manual de usuario.

Además, todo el código fuente se encuentra comentado (en inglés).

Soporte técnico
---------------

Si experimentas algún problema al utilizar CygnusCloud, utiliza la herramienta de seguimiento de issues
de este repositorio para avisarnos. Intentaremos corregirlo tan pronto como sea posible.

Cómo contribuir
---------------
Si quieres ayudarnos a mejorar CygnusCloud, envíanos una pull request con tus modificaciones: estaremos encantados
de estudiarla.

Readme (English version)
========================

Brief project description
-------------------------
CygnusCloud is a Master Thesis project co-developed by Luis Barrios, Adrián Fernández and Samuel Guayerbas,
students of Computer Engineering at the Complutense University of Madrid.

With CygnusCloud, we want to turn every underutilized computer room in the campus into a Computer Science lab.
This will allow students to work on their assignments out of the specialized computer rooms of their schools.

Furthermore, CygnusCloud also offers other benefits:
* Costs savings. CygnusCloud allows the usage of cheaper and less energy-consuming PCs on the computer rooms.
* Less bureaucracy. Nowadays, if a teacher wants to install a program on a computer room, he/she'll have to wait 
  for an entire month. With CygnusCloud, teachers can install applications on their own virtual machines and
  deploy the new configurations within a few hours.

Directory tree
--------------
The main directories that you'll find on the CygnusCloud repository are:

* Arquitectura: this directory contains the preliminary architectural designs.
* Documentación interna:  this directory contains some manuals written by the CygnusCloud team that explain
  how to install and use the basic tools used during the development process. 
* Memoria: this directory contains the main project documentation source. All its content is written
  in LaTeX through LyX, and "Memoria.lyx" is the master file.
* src: this directory includes the latest stable version's source code. Its main subdirectories are 
  src/Infraestructura (this directory contains the CygnusCloud infrastructure's source) and src/web 
  (this directory contains the web application's source).

Although the source code is mostly written (and commented) in English, the project's documentation is written
in Spanish. If you don't speak Spanish and want to ask something to us, don't be shy!

And if you want to translate any part of the CygnusCloud documentation, just send us your translation. We'll
be glad to publish it (acknowledging that you are the translator, of course).

How to download and install CygnusCloud
---------------------------------------
The latest stable version (5.0.1) can be downloaded from our blog (http://cygnusclouducm.wordpress.com/descargas-v5-0-1/).
The installation and usage instructions are described on the project's documentation
(available at http://cygnusclouducm.files.wordpress.com/2013/06/memoria.pdf).
