# Guía de Contribución

Este documento proporciona una guía para realizar commits en este proyecto, enfocado en la documentación de scripts y la infraestructura en Google Cloud. El objetivo es mantener un historial de cambios claro y consistente.

## Mensajes de Commit

Utilizamos una adaptación de **Conventional Commits** para nuestros mensajes.

### Estructura del Mensaje

Cada mensaje de commit debe seguir la siguiente estructura:

\`\`\`
<tipo>[<ámbito opcional>]: <descripción>

[<cuerpo opcional>]

[<pie de página opcional>]
\`\`\`

### Componentes del Mensaje

1.  **Tipo**: Indica la naturaleza del cambio. Los tipos principales que usaremos son:
    *   `feat`: Para nuevas funcionalidades o scripts.
    *   `fix`: Para correcciones en scripts o configuraciones.
    *   `docs`: Para cambios exclusivos en la documentación (READMEs, guías, diagramas, etc.).
    *   `refactor`: Para reestructurar scripts o configuraciones sin cambiar su funcionalidad externa.
    *   `chore`: Tareas de mantenimiento, actualizaciones de configuración de GCP, etc.
    *   `revert`: Para revertir un commit anterior.
    *   `style`: Cambios menores de formato en scripts o documentos que no alteran la lógica.
    *   `infra`: Cambios relacionados con la infraestructura en Google Cloud (ej. Terraform, configuraciones de servicios).
    *   `config`: Cambios en archivos de configuración.
    *   `new`: Para la creación de nuevos archivos.

2.  **Ámbito (Opcional)**: Especifica la parte del proyecto afectada. Ejemplos: `BigData/Codigo_ETL`, `InteligenciaArtificial/Notebook_IA`, `Documentacion_general`, `GCP/Terraform`, `Scripts_Adicionales`.
    *   Ejemplo: `docs(BigData/Documentacion_BigData): actualizar modelo de datos`
    *   Ejemplo: `feat(GCP/CloudFunctions): añadir función para procesar archivos subidos`

3.  **Descripción**: Un resumen conciso del cambio en imperativo presente.
    *   Debe ser breve (idealmente no más de 50-70 caracteres).
    *   No debe comenzar con mayúscula.
    *   No debe terminar con un punto.
    *   Ejemplo: `añadir validación de datos de entrada`

4.  **Cuerpo (Opcional)**: Proporciona información contextual adicional sobre el cambio. Explica el "qué" y el "porqué" del cambio, no el "cómo". Separa el cuerpo de la descripción con una línea en blanco.

5.  **Pie de Página (Opcional)**: Se utiliza para referenciar issues o para indicar cambios que rompen la compatibilidad (`BREAKING CHANGE`).
    *   Ejemplo para referenciar un issue: `Closes #42`
    *   Ejemplo para un cambio rompedor:
        \`\`\`
        BREAKING CHANGE: la función `procesarDatos` ahora requiere un nuevo parámetro `configuracion`.
        \`\`\`

### Ejemplos de Mensajes de Commit

*   **Creación de un nuevo archivo:**
    \`\`\`
    new(Documentacion_general): añadir guía de estilo para markdown
    \`\`\`

*   **Nueva característica en un ámbito específico:**
    \`\`\`
    feat(InteligenciaArtificial/Notebook_IA): implementar algoritmo de clustering k-means
    \`\`\`

*   **Corrección de error con cuerpo explicativo:**
    \`\`\`
    fix(BigData/Codigo_ETL): corregir error de parsing en fechas con formato ISO

    Las fechas provenientes de la fuente X no siempre seguían el estándar ISO 8601,
    lo que causaba fallos en el pipeline. Se ha añadido lógica para manejar
    formatos de fecha alternativos.
    \`\`\`

*   **Cambio en la documentación:**
    \`\`\`
    docs: actualizar README con instrucciones de despliegue
    \`\`\`

*   **Refactorización sin cambio funcional visible:**
    \`\`\`
    refactor(InteligenciaArtificial/Scripts_IA): optimizar función de preprocesamiento de texto
    \`\`\`
*   **Cambio en infraestructura:**
    \`\`\`
    infra(GCP/VPC): configurar nueva subred para servicios de IA
    \`\`\`

## Proceso General

1.  **Rama**: Crea una nueva rama para tus cambios (ej. `git checkout -b docs/actualizar-readme-gcp`).
2.  **Commits**: Realiza commits atómicos y descriptivos siguiendo la convención.
3.  **Push**: Sube tus cambios a la rama remota.
4.  **Merge/Pull Request**: Si trabajas en equipo, considera usar Pull Requests para revisión. Para contribuciones individuales directas a `main` (o la rama principal), asegúrate de que los cambios son correctos antes de hacer push.

---

Mantener un historial de commits claro es beneficioso para todos los involucrados en el proyecto.
