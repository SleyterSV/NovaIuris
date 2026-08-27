/**
 * exportUtils.js
 * Utilidad profesional para exportar reportes directamente en PDF llamando al backend.
 */

export async function descargarPDFOficial(datos, tipo = 'NovaCase') {
  try {
    // 1. Llamar al backend de FastAPI
    // Ajusta la URL según la ruta de tu servidor local o de producción
    const response = await fetch('http://localhost:8000/api/export/pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tipo: tipo,
        datos: datos
      })
    });

    if (!response.ok) {
      throw new Error('Error al generar el PDF en el servidor');
    }

    // 2. Convertir la respuesta del servidor en un Blob de tipo PDF
    const blob = await response.blob();
    
    // 3. Crear una URL temporal y forzar la descarga en el navegador
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `NovaIuris_${tipo}_Oficial.pdf`; // Nombre del archivo descargado
    document.body.appendChild(a);
    a.click();
    
    // 4. Limpieza de memoria
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    return { success: true };
  } catch (error) {
    console.error("Error crítico exportando PDF:", error);
    return { success: false, error: error.message };
  }
}