Breve descripción del proyecto
------------------------------
CygnusCloud es un proyecto de fin de carrera desarrollado por Luis barrios, Adrián Fernández y Samuel Guayerbas,
alumnos de Ingeniería en informática de la Universidad Complutense de Madrid.

El objetivo de CygnusCloud es convertir las aulas de informática no especializadas repartidas por todo el campus 
de la complutense en laboratorios de informática. Esto permitirá a los estudiantes poder realizar las prácticas
de sus asignaturas fuera de las sobre-pobladas aulas de informáticas especializadas en sus correspondientes facultades.

Además, CygnusCloud ofrece otros beneficios tales como:
      - Ahorrar dinero a la universidad, pudiendo utilizar ordenadores más baratos y con un consumo inferior.
      - Reducir la burocracia. Hoy en día, si un profesor quiere un prograama específico para la realización
        de alguna de sus prácticas, tendrá que esperar al menos un mes para poder disponer de dicho programa.
	Con CygnusCloud los profesores podrán instalar aplicaciones directamente en sus propias máquinas virtuales,
	y dar acceso a ellas en pocas horas.

Para conseguir esto, CygnusCloud dispone de una infraestructura orgaanizada en 3 grandes grupos e máquinas:
      - Los servidores de máquinas virtuales. Son los encargados de hospedar las diferentes máquinas virtuales.
      - El servidor de Cluster. Es el encargado de gestionar los servidores de máquinas virtuales y su interacción
        con los usuarios.
      -	El servidor web. Alberga el sitio web que permite a los usuarios ejecutar y gestionar las máquinas virtuales.

Arbol de directorios de CygnusCloud
-----------------------------------
Los principales directorios que podemos encontrar en el Repositorio de CygnusCloud son:

    - Arquitectura : Incluye un conjunto de documentos escritos durante el desarrollo del proyecto
      con los diseños de la arquitectura realizados.
    - Documentación interna:  Incluye un conjunto de manuales escritos por nosotros que explican de forma
      sencilla como instalar y utilizar las diferentes herramientas utilizadas durante el desarrollo
    - Memoria: Incluye la memoria del proyecto escrita hasta el momento. En ella, se define de forma 
      detallada todos los aspectos relacionados con CygnusCloud. Toda la memoria se encuentra escritaa en 
      lyx, siendo el fichero "Memoria.lyx" el fichero principal. 
    - src: Incluye todo el código fuente estable desarrollado hasta el momento. En su interior podemos
      destacar dos subdirectorios relevantes. 
    - src/CygnusCloud: Incluye todo el código relacionado con los servidores de máquinas virtuales y 
      el servidor de cluster. 
    - src/web: Incluye todo el código relacionado con el servidor web.

Como descargar CygnusCloud
--------------------------
Actualmente, puede descargarse la versión 1.0+ de CygnusCloud desde la página de descarga del blog 
(http://cygnusclouducm.wordpress.com/descargas/)
Los ejecutables están divididos en 3 tarballs diferentes y su instalación y uso viene explicado en el manual
 de usuario (disponible en http://cygnusclouducm.files.wordpress.com/2013/04/manualusuario_libro.pdf)
Si se desea obtener una versión estable más reciente del proyecto, puede realizarse un pull de la rama
develop del repositorio. Todo el código fuente se encuentra en el directorio src


Dependencias de CygnusCloud
---------------------------
Todas las dependencias necesarias para poder ejecutar CygnusCloud vienen detalladas en la sección 1 
del manual de usuario (disponible en http://cygnusclouducm.files.wordpress.com/2013/04/manualusuario_libro.pdf)
En la página de descargas del blog (http://cygnusclouducm.wordpress.com/descargas/) pueden accederse a las páginas
de descarga de las principales herramientas requeridas.

Instalación de CygnusCloud
--------------------------
Todos los pasos de instalación necesarios paraa poder utilizar CygnusCloud sin problemas vienen detallados en la 
sección 2 del manual de usuario (disponible en http://cygnusclouducm.files.wordpress.com/2013/04/manualusuario_libro.pdf)
Además la sección 3 explica como pueden crearse las máquinas virtuales que son gestionadas y ejecutadas por los usuarios
de CygnusCloud.
Por último, la sección 4 incluye una breve guia sobre el manejo de la web de CygnusCloud.

Documentación
-------------
Toda la documentación escrita sobre el proyecto se encuentra accesible en los directorios Memoria y Documentación Interna
del repositorio (en formato Lyx). 
Además, el blog de CygnusCloud (http://cygnusclouducm.wordpress.com/) contiene, además de todas las entradas escritas durante
el desarrollo del proyecto, una sección de manuales (http://cygnusclouducm.wordpress.com/manuales/) con los principales manuales
compilados en formato pdf y una sección de descargas (http://cygnusclouducm.wordpress.com/descargas/) con un completo manual de
usuario.

Información adicional
---------------------
Gracias a la entrega de nuestro director de proyecto, CygnusCloud ha sido dado a conocer en diferentes revistas y canales de radio:

    - El programa "Hoy por hoy" de la cadena Ser nos entrevistó junto a otros compañeros de carrera y nos permitió dar a conocer 
      los beneficios que CygnusCloud puede ofrecer. La entrevista se encuentra disponible aquí : 
	    http://www.cadenaser.com/cultura/audios/noticias-madrid-charlamos-proyectos-universidad/csrcsrpor/20130115csrcsrcul_8/Aes/
    - La prestigiosa publicación HPC in the Cloud  publicó un artículo sobre CygnusCloud. Puede leerse en la dirección:
	    http://www.hpcinthecloud.com/hpccloud/2013-01-04/student_projects_highlight_cloud_s_potential.html
    - La página de la facultad de Informática de la Universidad Complutense de Madrid publicó también un artículo sobre CygnusCloud
      que pude leerse en la siguiente dirección: http://www.fdi.ucm.es/Documento.asp?cod=1006





