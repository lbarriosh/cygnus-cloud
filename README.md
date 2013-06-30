Breve descripción del proyecto
------------------------------
CygnusCloud es un proyecto de fin de carrera desarrollado por Luis Barrios, Adrián Fernández y Samuel Guayerbas,
alumnos de Ingeniería en informática de la Universidad Complutense de Madrid.

El objetivo de CygnusCloud es convertir las aulas de informática no especializadas repartidas por todo el campus 
de la Complutense en laboratorios de informática. Esto permitirá a los estudiantes poder realizar las prácticas
de sus asignaturas fuera de las sobreutilizadas aulas de informáticas especializadas de sus correspondientes facultades.

Además, CygnusCloud ofrece otros beneficios:
* Ahorro de costes. Es posible utilizar ordenadores más baratos y con un consumo eléctrico inferior.
* Menos burocracia. Hoy en día, si un profesor quiere instalar un programa específico para la realización
  de alguna de sus prácticas, tendrá que esperar al menos un mes para poder disponer de dicho programa.
  Con CygnusCloud los profesores podrán instalar aplicaciones directamente en sus propias máquinas virtuales,
  y dar acceso a ellas en pocas horas.

Para conseguir esto, CygnusCloud utiliza una infraestructura formada por cuatro tipos de máquina:
* Los servidores de máquinas virtuales, que alojan las distintas máquinas virtuales.
* El repositorio de imágenes, que aloja las imágenes de disco de todas las máquinas virtuales que pueden utilizarse
  en la infraestructura.
* El servidor de cluster, que realiza el balanceado de carga entre los servidores de máquinas virtuales y se
  ocupa de la gestión de estas máquinas.
* El servidor web, que alberga la aplicación web que utilizarán los usuarios para interactuar con CygnusCloud.

Árbol de directorios de CygnusCloud
-----------------------------------
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

Cómo descargar e instalar CygnusCloud
-------------------------------------
Actualmente, puede descargarse la versión 5.0.1 de CygnusCloud desde la página de descarga de nuestro blog 
(http://cygnusclouducm.wordpress.com/descargas-v5-0-1/).
Cada tipo de máquina tiene asignado un tarball distinto. Las instrucciones de instalación y uso
se describen en la memoria del proyecto (disponible en http://cygnusclouducm.files.wordpress.com/2013/06/memoria.pdf).

Documentación
-------------
La memoria del proyecto (disponible en http://cygnusclouducm.files.wordpress.com/2013/06/memoria.pdf) incluye
el diseño detallado de CygnusCloud y su manual de usuario.

Además, todo el código fuente se encuentra comentado (en inglés).
