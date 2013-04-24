Breve descripción del proyecto
------------------------------
CygnusCloud es un proyecto de fin de carrera desarrollado por Luis Barrios, Adrián Fernández y Samuel Guayerbas,
alumnos de Ingeniería en informática de la Universidad Complutense de Madrid.

El objetivo de CygnusCloud es convertir las aulas de informática no especializadas repartidas por todo el campus 
de la Complutense en laboratorios de informática. Esto permitirá a los estudiantes poder realizar las prácticas
de sus asignaturas fuera de las sobreutilizadas aulas de informáticas especializadas de sus correspondientes facultades.

Además, CygnusCloud ofrece otros beneficios tales como:
      - Ahorrar dinero a la universidad, pudiendo utilizar ordenadores más baratos y con un consumo eléctrico inferior.
      - Reducir la burocracia. Hoy en día, si un profesor quiere instalar un programa específico para la realización
        de alguna de sus prácticas, tendrá que esperar al menos un mes para poder disponer de dicho programa.
	Con CygnusCloud los profesores podrán instalar aplicaciones directamente en sus propias máquinas virtuales,
	y dar acceso a ellas en pocas horas.

Para conseguir esto, CygnusCloud dispone de una infraestructura orgaanizada en tres grandes grupos de máquinas:
      - Los servidores de máquinas virtuales. Son los encargados de hospedar las diferentes máquinas virtuales.
      - El servidor de cluster. Es el encargado de realizar el balanceado de carga entre los servidores de máquinas virtuales
	y monitorizar su estado.
      -	El servidor web. Alberga el sitio web que permite a los usuarios ejecutar y gestionar las máquinas virtuales.

Árbol de directorios de CygnusCloud
-----------------------------------
Los principales directorios que podemos encontrar en el repositorio de CygnusCloud son:

    - Arquitectura : Incluye un conjunto de documentos escritos durante el desarrollo del proyecto
      con los diseños preliminares de la arquitectura realizados.
    - Documentación interna:  Incluye un conjunto de manuales escritos por nosotros que explican de forma
      sencilla cómo instalar y utilizar las diferentes herramientas utilizadas en el desarrollo del proyecto.
    - Memoria: Incluye la memoria del proyecto escrita hasta el momento. En ella, se define de forma 
      detallada todos los aspectos relacionados con CygnusCloud. Toda la memoria se encuentra escrita LaTeX
      usando LyX, siendo "Memoria.lyx" el fichero principal. 
    - src: Incluye todo el código fuente estable desarrollado hasta el momento. En su interior podemos
      destacar dos subdirectorios relevantes:
	- src/CygnusCloud: Incluye todo el código relacionado con los servidores de máquinas virtuales y 
	  el servidor de cluster. 
	- src/web: Incluye todo el código relacionado con el servidor web.

Cómo descargar CygnusCloud
--------------------------
Actualmente, puede descargarse la versión 1.0+ de CygnusCloud desde la página de descarga de nuestro blog 
(http://cygnusclouducm.wordpress.com/descargas/).
Los ejecutables están divididos en tres tarballs diferentes y su instalación y uso viene explicado en el manual
de usuario (disponible en http://cygnusclouducm.files.wordpress.com/2013/04/manualusuario_libro.pdf)
Si se desea obtener una versión estable más reciente del proyecto, puede realizarse un pull de la rama
develop del repositorio. Todo el código fuente se encuentra en el directorio src.

Dependencias de CygnusCloud
---------------------------
Todas las dependencias necesarias para poder ejecutar CygnusCloud vienen detalladas en la sección 1 
del manual de usuario (disponible en http://cygnusclouducm.files.wordpress.com/2013/04/manualusuario_libro.pdf).
Desde la página de descargas del blog (http://cygnusclouducm.wordpress.com/descargas/) puede accederse a las páginas
de descarga de las principales herramientas requeridas.

Instalación de CygnusCloud
--------------------------
Todos los pasos de instalación necesarios para poder utilizar CygnusCloud sin problemas vienen detallados en la 
sección 2 del manual de usuario (disponible en http://cygnusclouducm.files.wordpress.com/2013/04/manualusuario_libro.pdf).
Además, la sección 3 explica cómo pueden crearse las máquinas virtuales que utilizan los usuarios de CygnusCloud.
Por último, la sección 4 incluye una breve guía de uso de la web de CygnusCloud.

Documentación
-------------
Toda la documentación escrita sobre el proyecto se encuentra accesible en los directorios Memoria y Documentación Interna
del repositorio (en formato LyX). 
Por otra parte el blog de CygnusCloud (http://cygnusclouducm.wordpress.com/) contiene, además de todas las entradas escritas durante
el desarrollo del proyecto, una sección de manuales (http://cygnusclouducm.wordpress.com/manuales/) con parte de la documentación interna
compilada en formato pdf y una sección de descargas (http://cygnusclouducm.wordpress.com/descargas/) con un completo manual de
usuario.

Información adicional
---------------------
Gracias a la entrega de nuestro director de proyecto, CygnusCloud se ha dado a conocer en diferentes revistas y canales de radio:

    - El programa "Hoy por hoy" de la cadena Ser nos entrevistó junto a otros compañeros de la Facultad y nos permitió dar a conocer 
      los beneficios que CygnusCloud puede ofrecer. La entrevista se encuentra disponible aquí: 
	    http://www.cadenaser.com/cultura/audios/noticias-madrid-charlamos-proyectos-universidad/csrcsrpor/20130115csrcsrcul_8/Aes/
    - La prestigiosa publicación HPC in the Cloud publicó en portada un artículo sobre CygnusCloud, y lo mantuvo durante un mes. 
      Ese artículo puede consultarse en la dirección
	    http://www.hpcinthecloud.com/hpccloud/2013-01-04/student_projects_highlight_cloud_s_potential.html
    - La página de la Facultad de Informática de la Universidad Complutense de Madrid publicó también un artículo sobre CygnusCloud
      que pude leerse en http://www.fdi.ucm.es/Documento.asp?cod=1006
    - El periódico de la Universidad Complutense, Tribuna Complutense, publicó un artículo en el que se mencionan los objetivos principales
      de CygnusCloud. Puede leerse en http://cygnusclouducm.files.wordpress.com/2013/01/tribunacomplutense.pdf.
    - A fecha de 24/04/13, el blog de CygnusCloud cuenta con más de 1800 visitas, contando con tráfico procedente de muchos lugares de Europa
      y Sudamérica.