# MYKE — Fase 2.1D: Auth y correo

## Estado de la inspección

| Área | Estado encontrado |
|---|---|
| Registro, login y logout | Implementados con `supabase-js`; confirmación obligatoria ya estaba activa en Supabase local |
| Sesión y renovación | Implementadas mediante persistencia y renovación nativas del SDK; el token de acceso se propaga al backend |
| Recuperación | Solicitud y cambio implementados; el callback `PASSWORD_RECOVERY` activa la vista de nueva contraseña |
| Reenvío de confirmación | Incorporado en esta fase con respuesta neutral y bloqueo de doble envío en UI |
| Enlaces inválidos/expirados | Mensaje público seguro incorporado; error original de Auth no se presenta |
| Plantillas | Plantillas MYKE locales para confirmación y recuperación |
| Proveedor SMTP externo | Bloqueado: no hay credenciales de pruebas ni proveedor autorizado disponible en el entorno |

## Versiones y configuración local

- Supabase CLI: `2.122.0`.
- `@supabase/supabase-js`: `2.117.2`.
- Auth local requiere confirmación de correo, usa rotación de refresh token y expiración OTP de una hora.
- El SMTP local predeterminado captura en Mailpit (`[local_smtp]`); no envía correo externo.
- Las rutas de la aplicación son `http://localhost:5173` y `http://127.0.0.1:5173`.
- El SDK conserva su flujo PKCE predeterminado para recuperación. El callback de contraseña redirige a `/?auth_action=reset`.
- El logout cierra la sesión local del navegador. No afirma revocar access tokens ya emitidos en otros dispositivos.

## Proveedor SMTP externo de pruebas

No se configuraron ni probaron credenciales reales. Para probar un SMTP de sandbox autorizado con Supabase CLI, se requieren estas variables en un `.env` local ignorado por Git, en la raíz del repositorio:

```dotenv
MYKE_AUTH_SMTP_HOST=smtp.example.test
MYKE_AUTH_SMTP_USER=usuario_sandbox
MYKE_AUTH_SMTP_PASSWORD=secreto_sandbox
MYKE_AUTH_SMTP_FROM_ADDRESS=no-reply@example.test
```

Una vez autorizado el proveedor, habilitar temporalmente en `supabase/config.toml` `[auth.email.smtp]`; el bloque comentado ya mapea `host`, `user`, `pass` y `admin_email` a `env(MYKE_AUTH_SMTP_...)`. Ajustar `port` (587 por defecto) al proveedor y mantener `sender_name = "MYKE Legal Intelligence"`. Reiniciar solo la instancia local para tomar la configuración. No llevar estas credenciales al frontend ni al repositorio. El sandbox debe aceptar únicamente destinatarios controlados por el operador. No añadir credenciales SMTP a `.env.example` ni al historial Git.

No se crearon cuentas, no se modificó DNS y no se contactó a un proveedor externo.

## Plantillas

`supabase/templates/confirmation.html` y `recovery.html` usan variables oficiales de Supabase `{{ .ConfirmationURL }}`. Ambas incluyen botón, enlace alternativo accesible, aviso de seguridad y estilos inline aptos para clientes de correo.

## Seguridad y límites

- Las respuestas de recuperación y reenvío no confirman si una dirección tiene cuenta.
- Los errores de proveedor se traducen a mensajes genéricos; errores de correo no se registran con cuerpos ni credenciales.
- El navegador compara las dos contraseñas; Supabase Auth sigue siendo quien valida y persiste la nueva contraseña.
- Se distingue entre revocación local del refresh session y validez temporal de access JWT ya emitidos. No se promete logout global.
- El envío real externo, el recorrido visual completo del navegador y el restablecimiento real quedan pendientes de SMTP de sandbox y navegador automatizable.

## Procedimiento de validación externa pendiente

1. Entregar al operador una cuenta de prueba controlada en un proveedor SMTP sandbox y configurar las cinco variables anteriores en `.env` local.
2. Aplicar temporalmente el bloque SMTP desde `env()` y reiniciar la instancia **local** de Supabase.
3. Ejecutar MYKE local con URL/key publicables locales, registrar un correo de prueba controlado y confirmar recepción en el proveedor sandbox.
4. Probar el enlace de confirmación, reenvío, solicitud de recuperación, cambio de contraseña, rechazo del enlace usado/expirado y login con contraseña nueva.
5. Probar logout local y acceso a `/api/me`/casos con sesión cerrada; repetir con dos usuarios de prueba y comprobar que el segundo recibe 404/403 al solicitar recursos del primero.
6. Confirmar que no aparecen secretos, tokens, enlaces activos ni datos personales en logs o capturas.

La entrega mediante Mailpit valida la integración local de Auth y la plantilla, pero no equivale a entrega SMTP real.
