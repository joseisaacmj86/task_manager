
$(document).ready(function () {

    // Abrir el modal de nueva tarea
    $("a[href='/tasks/create']").on("click", function (event) {
        event.preventDefault(); // Evita la redirección
        $("#nuevaTareaModal").css("display", "block");
    });

    // Cerrar el modal con cualquier botón de cierre
    $("#closeModalBtn, #closeModalBtn2").on("click", function () {
        $("#nuevaTareaModal").css("display", "none");
    });

    // Cerrar el modal al hacer clic fuera de él
    $(window).on("click", function (event) {
        if ($(event.target).is("#nuevaTareaModal")) {
            $("#nuevaTareaModal").css("display", "none");
        }
    });


    // Crear nueva tarea
    $('#createTaskForm').on('submit', function (e) {
        e.preventDefault();
    
        const title = $('#title').val();
        const description = $('#description').val();
        const task = { title, description };
    
        $.ajax({
            url: '/tasks',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(task),
            success: function () {
                alert('Tarea creada exitosamente');
                $('#title').val('');
                $('#description').val('');
                window.location.reload();
            },
            error: function (xhr) {
                console.error('Error:', xhr.responseText);
                alert('Error al crear la tarea');
            }
        });
    });


    // eliminar tarea
    $(document).on("click", ".delete-task", function (e) {
        e.preventDefault();
    
        // Obtener el ID de la tarea desde el atributo href
        const taskUrl = $(this).attr("href");
        const taskId = taskUrl.split("/").pop();
    
        if (confirm("¿Estás seguro de que deseas eliminar esta tarea?")) {
            $.ajax({
                url: `/tasks/${taskId}`,
                type: 'DELETE',
                success: function () {
                    alert('Tarea eliminada exitosamente');
                    location.reload();
                },
                error: function (xhr) {
                    console.error('Error:', xhr.responseText);
                    alert('Error al eliminar la tarea');
                }
            });
        }
    });

   
    // Abrir el modal de edición
    $(document).on("click", ".edit-task", function (event) {
        event.preventDefault();
        
        // Obtener el task_id desde el atributo href
        const taskUrl = $(this).attr("href");
        const taskId = taskUrl.split("/").pop();

        // Realizar la solicitud GET para obtener la tarea
        $.ajax({
            url: `/tasks/${taskId}`,
            type: 'GET',
            success: function (task) {
                // Llenar los campos del modal con la información de la tarea
                $('#editTaskId').val(task.task_id);
                $('#editTitle').val(task.title);
                $('#editDescription').val(task.description);

                // Abrir el modal de edición
                $('#editarTareaModal').css("display", "block");
            },
            error: function (xhr) {
                console.error('Error:', xhr.responseText);
                alert('Error al cargar la tarea');
            }
        });
    });

    // Cerrar el modal de edición
    $("#closeModalBtnEditar, #closeModalBtnEditar2").on("click", function () {
        $("#editarTareaModal").css("display", "none");
    });

    // Cerrar el modal al hacer clic fuera de él
    $(window).on("click", function (event) {
        if ($(event.target).is("#editarTareaModal")) {
            $("#editarTareaModal").css("display", "none");
        }
    });


    // Actualizar la tarea
    $('#editTaskForm').on('submit', function (e) {
        e.preventDefault();

        const taskId = $('#editTaskId').val();
        const title = $('#editTitle').val();
        const description = $('#editDescription').val();
        const updatedTask = { title, description };

        $.ajax({
            url: `/tasks/${taskId}`,
            type: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify(updatedTask),
            success: function () {
                alert('Tarea actualizada exitosamente');
                window.location.reload(); 
            },
            error: function (xhr) {
                console.error('Error:', xhr.responseText);
                alert('Error al actualizar la tarea');
            }
        });
    });

    // Descargar archivo JSON con las tareas (Exportar)
    $(document).on('click', '#exportTasks', function (e) {
        e.preventDefault();
    
        $.ajax({
            url: '/action/export',
            type: 'GET',
            dataType: 'binary', // Evita el manejo automático de JSON
            processData: false,
            xhrFields: {
                responseType: 'blob'
            },
            success: function (blob, status, xhr) {
                // Obtener el nombre del archivo desde los encabezados
                const contentDisposition = xhr.getResponseHeader('Content-Disposition');
                const filename = contentDisposition
                    ? contentDisposition.split('filename=')[1].replace(/"/g, '') // Limpia el nombre del archivo
                    : 'downloaded_file.json';
    
                // Crear una URL para descargar el archivo
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
    
                // Revocar la URL para liberar memoria
                window.URL.revokeObjectURL(url);
            },
            error: function (xhr, status, error) {
                console.error('Error durante la exportación:', error);
                alert('No se pudo exportar el archivo.');
            }
        });
    });
    

    // Mostrar el modal para importar tareas
    $(document).on('click', '#importTasks', function (e) {
        e.preventDefault();
        $('#importModal').css('display', 'block');
    });

    // Cerrar el modal de importar tareas
    $(document).on('click', '.close-modal', function () {
        $('#importModal').css('display', 'none');
    });


    // Importar archivo JSON de tareas
    $(document).on('submit', '#importForm', function (e) {
        e.preventDefault();

        const fileInput = $('#importFile')[0];
        if (fileInput.files.length === 0) {
            alert('Por favor, selecciona un archivo JSON.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        $.ajax({
            url: '/action/import',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function (response) {
                alert(`Importación completada. Tareas importadas: ${response.imported_tasks}. Tareas omitidas: ${response.skipped_tasks}`);
                $('#importModal').css('display', 'none');
                location.reload();
            },
            error: function (xhr) {
                console.error('Error:', xhr.responseText);
                alert('Error al importar las tareas');
            }
        });
    });

    //cambiar tarea de estado.
    $(document).on("click", ".complete-task", function (event) {
        event.preventDefault();
    
        const taskUrl = $(this).attr("href");
        const taskId = taskUrl.split("/").pop();
    
        // Determina el nuevo estado basado en el texto del botón
        const button = $(this).find("button");
        const newStatus = button.text().trim();
    
        // Realiza la solicitud PUT con el estado como query parameter
        $.ajax({
            url: `/tasks/complete/${taskId}?status=${newStatus}`, // Enviar el estado como parámetro
            type: 'PUT',
            success: function (task) {
                window.location.reload();
                //button.text(task.status === "TERMINADA" ? "Pendiente" : "Terminada");
            },
            error: function (xhr) {
                console.error('Error:', xhr.responseText);
                alert('Error al cambiar el estado de la tarea');
            }
        });
    });

    $('table tbody tr').each(function() {
        var status = $(this).find('td:eq(4)').text().trim();        
        
        if (status !== 'TERMINADA') {
            $(this).find('.delete-task button')
                    .prop('disabled', true)
                    .addClass('btn-secondary disabled')
                    .removeClass('btn-danger')
                    .css('opacity', '0.65');
        }
    });

    
});
